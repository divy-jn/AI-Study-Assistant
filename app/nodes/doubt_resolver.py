"""
Doubt Clarification Node
Answers conceptual questions and clarifies doubts using uploaded notes
"""
from typing import Dict, Any, Optional
from app.core.state import GraphState

from app.core.logging_config import get_logger, LogExecutionTime
from app.services.llm_service import get_llm_service
from app.core.exceptions import WorkflowNodeException
from app.core.prompts import (
    DOUBT_RESOLVER_SYSTEM,
    DOUBT_RESOLVER_NOTES_PROMPT,
    DOUBT_RESOLVER_GENERAL_SYSTEM,
    DOUBT_RESOLVER_GENERAL_PROMPT
)


logger = get_logger(__name__)


class DoubtResolver:
    """
    Resolves student doubts and answers conceptual questions
    Prioritizes uploaded notes, falls back to general knowledge when needed
    """
    
    def __init__(self):
        self.logger = logger
    
    async def resolve(self, state: GraphState) -> GraphState:
        """
        Resolve doubt/answer question
        
        Args:
            state: Current graph state
            
        Returns:
            Updated state with answer
        """
        query = state["query"]
        context = state.get("context", "")
        doc_types = state.get("document_types_available", [])
        retrieved_docs = state.get("retrieved_documents", [])
        
        self.logger.info(
            f"❓ Resolving doubt | "
            f"Query: '{query[:100]}' | "
            f"Context available: {bool(context)}"
        )
        
        with LogExecutionTime(self.logger, "Doubt resolution"):
            try:
                # Determine if we have relevant notes
                has_relevant_notes = self._check_relevance(retrieved_docs)
                
                if has_relevant_notes:
                    # Answer from notes
                    answer, source_type = await self._answer_from_notes(
                        query, context
                    )
                else:
                    # Fallback to general knowledge
                    answer, source_type = await self._answer_from_general_knowledge(
                        query
                    )
                
                # Format the response
                formatted_response = self._format_response(
                    answer, source_type, has_relevant_notes
                )
                
                # Update state
                state["final_response"] = formatted_response
                state["task_data"]["source_type"] = source_type
                state["task_data"]["has_relevant_notes"] = has_relevant_notes
                state["nodes_visited"].append("doubt_resolver")
                
                self.logger.info(
                    f"✅ Doubt resolved | "
                    f"Source: {source_type} | "
                    f"Length: {len(answer)} chars"
                )
                
                return state
                
            except Exception as e:
                self.logger.error(f"❌ Doubt resolution failed: {str(e)}", exc_info=True)
                raise WorkflowNodeException(
                    node_name="doubt_resolver",
                    reason=str(e),
                    original_exception=e
                )
    
    def _check_relevance(self, retrieved_docs: list) -> bool:
        """
        Check if retrieved documents are relevant
        
        Args:
            retrieved_docs: List of retrieved documents
            
        Returns:
            True if relevant notes found
        """
        if not retrieved_docs:
            return False
        
        # Check if any document has good similarity score
        relevant_count = sum(
            1 for doc in retrieved_docs
            if doc.get("similarity_score", 0) >= 0.7
        )
        
        # Consider relevant if at least 2 documents have high similarity
        return relevant_count >= 2
    
    async def _answer_from_notes(
        self,
        query: str,
        context: str
    ) -> tuple[str, str]:
        """
        Answer question using uploaded notes
        
        Returns:
            (answer, source_type)
        """
        llm_service = await get_llm_service()
        
        prompt = DOUBT_RESOLVER_NOTES_PROMPT.format(query=query, context=context)
        
        system_prompt = DOUBT_RESOLVER_SYSTEM
        
        answer = await llm_service.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=1500
        )
        
        return answer.strip(), "notes"
    
    async def _answer_from_general_knowledge(
        self,
        query: str
    ) -> tuple[str, str]:
        """
        Answer question using LLM's general knowledge
        
        Returns:
            (answer, source_type)
        """
        llm_service = await get_llm_service()
        
        prompt = DOUBT_RESOLVER_GENERAL_PROMPT.format(query=query)
        
        system_prompt = DOUBT_RESOLVER_GENERAL_SYSTEM
        
        answer = await llm_service.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.8,
            max_tokens=1500
        )
        
        return answer.strip(), "general_knowledge"
    
    def _format_response(
        self,
        answer: str,
        source_type: str,
        has_relevant_notes: bool
    ) -> str:
        """
        Format the final response with appropriate disclaimer
        
        Args:
            answer: Generated answer
            source_type: Type of source used
            has_relevant_notes: Whether notes were relevant
            
        Returns:
            Formatted response
        """
        # Add header based on source
        if source_type == "notes":
            header = "## Answer (Based on Your Notes)\n\n"
            footer = "\n\n---\n📚 *This answer is based on your uploaded notes.*"
        else:
            header = "## Answer\n\n"
            footer = "\n\n---\n⚠️ *This answer is based on general knowledge as your uploaded notes don't contain sufficient information on this topic. Please verify with your study materials.*"
        
        return header + answer + footer


# Global instance
_doubt_resolver = DoubtResolver()


async def resolve_doubt_node(state: GraphState) -> GraphState:
    """
    LangGraph node function for doubt resolution
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with answer
    """
    return await _doubt_resolver.resolve(state)


if __name__ == "__main__":
    import asyncio
    from langgraph_state import create_initial_state
    
    async def test():
        # Test with notes context
        state1 = create_initial_state(
            user_id=1,
            query="What is supervised learning?"
        )
        
        state1["context"] = """
--- NOTES ---
Supervised learning is a type of machine learning where the model learns from labeled data.
The training data includes both input features and corresponding output labels.
Common algorithms include linear regression, logistic regression, and decision trees.
Examples: Email spam classification, house price prediction.
"""
        
        state1["document_types_available"] = ["notes"]
        state1["retrieved_documents"] = [
            {"similarity_score": 0.85, "chunk_text": "Supervised learning..."}
        ]
        
        result1 = await resolve_doubt_node(state1)
        
        print("\n" + "="*60)
        print("TEST 1: Answer from Notes")
        print("="*60)
        print(result1["final_response"])
        print("="*60)
        
        # Test without relevant notes
        state2 = create_initial_state(
            user_id=1,
            query="What is quantum computing?"
        )
        
        state2["context"] = ""
        state2["document_types_available"] = []
        state2["retrieved_documents"] = []
        
        result2 = await resolve_doubt_node(state2)
        
        print("\n" + "="*60)
        print("TEST 2: Answer from General Knowledge")
        print("="*60)
        print(result2["final_response"][:500] + "...")
        print("="*60)
    
    asyncio.run(test())
