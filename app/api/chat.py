"""
Chat API Router
Handles user queries and integrates with LangGraph workflow
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import sqlite3
from datetime import datetime

from app.core.logging_config import get_logger
from app.workflows.graph import process_user_query
from .auth import get_current_user
from app.services.llm_service import get_llm_service, OllamaLLMService


logger = get_logger(__name__)
router = APIRouter()


# ============================================================================
# Request/Response Models
# ============================================================================

class ChatRequest(BaseModel):
    """Chat request model"""
    query: str
    conversation_id: Optional[int] = None


class ChatResponse(BaseModel):
    """Chat response model"""
    success: bool
    intent: str
    response: Optional[str] = None
    answer: Optional[str] = None
    evaluation: Optional[Dict[str, Any]] = None
    questions: Optional[List[Dict[str, Any]]] = None
    processing_time: float
    metadata: Dict[str, Any]


class ConversationResponse(BaseModel):
    """Conversation history response"""
    conversation_id: int
    started_at: str
    last_message_at: str
    message_count: int


# ============================================================================
# Helper Functions
# ============================================================================

def get_db():
    """Get database connection"""
    conn = sqlite3.connect("./data/sqlite.db")
    conn.row_factory = sqlite3.Row
    return conn


def create_conversation(user_id: int) -> int:
    """
    Create a new conversation
    
    Args:
        user_id: User ID
        
    Returns:
        Conversation ID
    """
    conn = get_db()
    cursor = conn.cursor()
    
    import uuid
    session_id = str(uuid.uuid4())
    
    cursor.execute(
        """
        INSERT INTO conversations (user_id, session_id)
        VALUES (?, ?)
        """,
        (user_id, session_id)
    )
    
    conn.commit()
    conversation_id = cursor.lastrowid
    conn.close()
    
    return conversation_id


def save_message(
    conversation_id: int,
    role: str,
    content: str,
    intent: Optional[str] = None,
    metadata: Optional[Dict] = None
):
    """
    Save a message to conversation history
    
    Args:
        conversation_id: Conversation ID
        role: Message role (user/assistant)
        content: Message content
        intent: Detected intent
        metadata: Additional metadata
    """
    conn = get_db()
    cursor = conn.cursor()
    
    import json
    metadata_json = json.dumps(metadata) if metadata else None
    
    cursor.execute(
        """
        INSERT INTO messages (conversation_id, role, content, intent, metadata)
        VALUES (?, ?, ?, ?, ?)
        """,
        (conversation_id, role, content, intent, metadata_json)
    )
    
    conn.commit()
    conn.close()


# ============================================================================
# API Endpoints
# ============================================================================


from fastapi.responses import StreamingResponse
import json

@router.post("/query", response_model=ChatResponse)
async def process_query(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
    llm_service: OllamaLLMService = Depends(get_llm_service)
):
    """
    Process a user query through the AI workflow
    
    Args:
        request: Chat request with query
        current_user: Current authenticated user
        
    Returns:
        AI response with answer/evaluation/questions
    """
    user_id = current_user["id"]
    query = request.query
    
    logger.info(
        f"💬 Processing query | "
        f"User: {user_id} | "
        f"Query: '{query[:100]}...'"
    )
    
    try:
        # Create conversation if needed
        conversation_id = request.conversation_id
        if not conversation_id:
            conversation_id = create_conversation(user_id)
        
        # Save user message
        save_message(
            conversation_id=conversation_id,
            role="user",
            content=query
        )
        
        # Process query through LangGraph workflow
        result = await process_user_query(
            user_id=user_id,
            query=query,
            conversation_id=conversation_id
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Query processing failed")
            )
        
        # Build response content
        response_content = ""
        if result.get("response"):
            response_content = result["response"]
        elif result.get("answer"):
            response_content = result["answer"]
        elif result.get("evaluation"):
            eval_result = result["evaluation"]
            response_content = f"Score: {eval_result['obtained_marks']}/{eval_result['total_marks']}\n\n{eval_result.get('feedback', '')}"
        
        # Save assistant message
        save_message(
            conversation_id=conversation_id,
            role="assistant",
            content=response_content,
            intent=result["intent"],
            metadata=result.get("metadata", {})
        )
        
        logger.info(
            f"✅ Query processed | "
            f"Intent: {result['intent']} | "
            f"Time: {result['processing_time']:.2f}s"
        )
        
        # Build response
        return ChatResponse(
            success=True,
            intent=result["intent"],
            response=result.get("response"),
            answer=result.get("answer"),
            evaluation=result.get("evaluation"),
            questions=result.get("questions"),
            processing_time=result["processing_time"],
            metadata=result.get("metadata", {})
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Query processing failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process query: {str(e)}"
        )



@router.post("/stream")
async def stream_query(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
    llm_service: OllamaLLMService = Depends(get_llm_service)
):
    """
    Stream a user query response using Server-Sent Events (SSE) with context
    """
    user_id = current_user["id"]
    query = request.query
    conversation_id = request.conversation_id
    
    logger.info(f"🌊 Streaming query | User: {user_id} | Query: '{query[:50]}...'")
    
    # Create conversation if needed
    if not conversation_id:
        conversation_id = create_conversation(user_id)
    
    # Save user message first so it's part of history for next time (but we manually add it for this turn)
    save_message(conversation_id=conversation_id, role="user", content=query)
    
    async def event_generator():
        try:
            # Emit status: Fetching history
            yield f"data: {json.dumps({'type': 'status', 'message': 'Fetching history...'})}\n\n"

            # 1. Fetch History (Last 10 messages)
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT role, content 
                FROM messages 
                WHERE conversation_id = ? 
                ORDER BY id DESC LIMIT 10
                """,
                (conversation_id,)
            )
            # Fetch and reverse to get chronological order
            history_rows = cursor.fetchall()[::-1]
            conn.close()
            
            messages = []
            
            # Emit status: Searching docs
            yield f"data: {json.dumps({'type': 'status', 'message': 'Searching knowledge base...'})}\n\n"

            # 2. Retrieve Documents (Simple RAG)
            from app.nodes.document_retriever import DocumentRetriever, Intent
            from app.core.state import create_initial_state
            
            # Setup simple retrieval state
            state = create_initial_state(user_id=user_id, query=query)
            state["intent"] = Intent.DOUBT_CLARIFICATION
            
            retriever = DocumentRetriever()
            await retriever.retrieve(state)
            
            context = state.get("context", "")
            retrieved_docs = state.get("retrieved_documents", [])
            
            # Send context info
            if retrieved_docs:
                yield f"data: {json.dumps({'type': 'info', 'message': f'Found {len(retrieved_docs)} relevant notes'})}\n\n"
            else:
                yield f"data: {json.dumps({'type': 'info', 'message': 'Using general knowledge'})}\n\n"

            # Emit status: Thinking
            yield f"data: {json.dumps({'type': 'status', 'message': 'Thinking...'})}\n\n"
            
            # 3. Build System Prompt & Messages
            from app.nodes.doubt_resolver import (
                DOUBT_RESOLVER_SYSTEM,
                DOUBT_RESOLVER_GENERAL_SYSTEM
            )
            
            # Decide system prompt based on context availability
            if context:
                system_prompt_text = DOUBT_RESOLVER_SYSTEM
                # Add context to the latest user message or as a system instruction?
                # Usually better to add as context in the last user message
                final_query = f"Context information is below.\n---------------------\n{context}\n---------------------\nGiven the context information and not prior knowledge, answer the query.\nQuery: {query}"
                encoded_source = "notes"
            else:
                system_prompt_text = DOUBT_RESOLVER_GENERAL_SYSTEM
                final_query = query
                encoded_source = "general_knowledge"

            # Add System Prompt
            messages.append({"role": "system", "content": system_prompt_text})
            
            # Add History (excluding the current message we just saved)
            if history_rows and history_rows[-1][1] == query:
                history_rows = history_rows[:-1]
                
            for row in history_rows:
                messages.append({"role": row[0], "content": row[1]})
            
            # Add current modified query
            messages.append({"role": "user", "content": final_query})
            
            # 4. Stream LLM Response
            full_response = ""
            async for chunk in llm_service.chat_stream(
                messages=messages,
                temperature=0.7,
                max_tokens=1500
            ):
                full_response += chunk
                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
            
            # 5. Save completed message
            save_message(
                conversation_id=conversation_id,
                role="assistant",
                content=full_response,
                intent="doubt_clarification",
                metadata={"source": encoded_source, "streamed": True}
            )
            
            # Final event
            yield f"data: {json.dumps({'type': 'done', 'conversation_id': conversation_id})}\n\n"
            
        except Exception as e:
            logger.error(f"❌ Streaming failed: {e}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")





@router.get("/conversations")
async def list_conversations(current_user: dict = Depends(get_current_user)):
    """
    List user's conversations
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        List of conversations
    """
    user_id = current_user["id"]
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        """
        SELECT 
            c.id,
            c.started_at,
            c.last_message_at,
            COUNT(m.id) as message_count
        FROM conversations c
        LEFT JOIN messages m ON c.id = m.conversation_id
        WHERE c.user_id = ?
        GROUP BY c.id
        ORDER BY c.last_message_at DESC
        LIMIT 20
        """,
        (user_id,)
    )
    
    conversations = []
    for row in cursor.fetchall():
        conversations.append({
            "conversation_id": row[0],
            "started_at": row[1],
            "last_message_at": row[2],
            "message_count": row[3]
        })
    
    conn.close()
    
    return {"conversations": conversations}


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Get conversation history
    
    Args:
        conversation_id: Conversation ID
        current_user: Current authenticated user
        
    Returns:
        Conversation messages
    """
    user_id = current_user["id"]
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Verify conversation belongs to user
    cursor.execute(
        "SELECT * FROM conversations WHERE id = ? AND user_id = ?",
        (conversation_id, user_id)
    )
    
    conversation = cursor.fetchone()
    if not conversation:
        conn.close()
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Get messages
    cursor.execute(
        """
        SELECT role, content, intent, timestamp
        FROM messages
        WHERE conversation_id = ?
        ORDER BY timestamp ASC
        """,
        (conversation_id,)
    )
    
    messages = []
    for row in cursor.fetchall():
        messages.append({
            "role": row[0],
            "content": row[1],
            "intent": row[2],
            "timestamp": row[3]
        })
    
    conn.close()
    
    return {
        "conversation_id": conversation_id,
        "messages": messages
    }


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a conversation
    
    Args:
        conversation_id: Conversation ID
        current_user: Current authenticated user
        
    Returns:
        Success message
    """
    user_id = current_user["id"]
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Verify and delete
    cursor.execute(
        "DELETE FROM conversations WHERE id = ? AND user_id = ?",
        (conversation_id, user_id)
    )
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    conn.commit()
    conn.close()
    
    logger.info(f"🗑️ Conversation deleted | ID: {conversation_id}")
    
    return {
        "message": "Conversation deleted successfully",
        "conversation_id": conversation_id
    }


if __name__ == "__main__":
    print("Chat API Router")
