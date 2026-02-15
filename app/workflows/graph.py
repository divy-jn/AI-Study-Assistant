"""
LangGraph Workflow - Main Orchestrator
Defines and compiles the complete workflow graph
"""
from langgraph.graph import StateGraph, END
from typing import Dict, Any
import time

from app.core.state import GraphState, create_initial_state, ProcessingStatus
from app.core.logging_config import get_logger, LogExecutionTime

# Import all nodes
from app.nodes.intent_classifier import classify_intent_node
from app.nodes.document_retriever import retrieve_documents_node
from app.nodes.answer_generator import generate_answer_node
from app.nodes.answer_evaluator import evaluate_answer_node
from app.nodes.doubt_resolver import resolve_doubt_node
from app.nodes.question_generator import generate_questions_node

# Import router
from app.nodes.router import route_after_intent, route_after_retrieval


logger = get_logger(__name__)


class WorkflowOrchestrator:
    """
    Main workflow orchestrator using LangGraph
    Manages the complete educational AI workflow
    """
    
    def __init__(self):
        self.logger = logger
        self.graph = self._build_graph()
        self.logger.info("🎯 LangGraph workflow initialized")
    
    def _build_graph(self) -> StateGraph:
        """
        Build the complete workflow graph
        
        Returns:
            Compiled StateGraph
        """
        self.logger.info("🔨 Building workflow graph...")
        
        # Initialize graph
        workflow = StateGraph(GraphState)
        
        # Add all nodes
        workflow.add_node("classify_intent", classify_intent_node)
        workflow.add_node("retrieve_documents", retrieve_documents_node)
        workflow.add_node("generate_answer", generate_answer_node)
        workflow.add_node("evaluate_answer", evaluate_answer_node)
        workflow.add_node("resolve_doubt", resolve_doubt_node)
        workflow.add_node("generate_questions", generate_questions_node)
        
        # Set entry point
        workflow.set_entry_point("classify_intent")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "classify_intent",
            route_after_intent,
            {
                "retrieve_documents": "retrieve_documents",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "retrieve_documents",
            route_after_retrieval,
            {
                "generate_answer": "generate_answer",
                "evaluate_answer": "evaluate_answer",
                "resolve_doubt": "resolve_doubt",
                "generate_questions": "generate_questions",
                "end": END
            }
        )
        
        # All task nodes end after execution
        workflow.add_edge("generate_answer", END)
        workflow.add_edge("evaluate_answer", END)
        workflow.add_edge("resolve_doubt", END)
        workflow.add_edge("generate_questions", END)
        
        # Compile graph
        compiled_graph = workflow.compile()
        
        self.logger.info("✅ Workflow graph built successfully")
        
        return compiled_graph
    
    async def process_query(
        self,
        user_id: int,
        query: str,
        conversation_id: int = None
    ) -> Dict[str, Any]:
        """
        Process a user query through the complete workflow
        
        Args:
            user_id: User ID
            query: User query
            conversation_id: Optional conversation ID
            
        Returns:
            Final workflow result with response
        """
        self.logger.info(
            f"🚀 Processing query | "
            f"User: {user_id} | "
            f"Query: '{query[:100]}...'"
        )
        
        start_time = time.time()
        
        try:
            # Create initial state
            initial_state = create_initial_state(
                user_id=user_id,
                query=query,
                conversation_id=conversation_id
            )
            
            initial_state["status"] = ProcessingStatus.IN_PROGRESS
            
            # Execute workflow
            with LogExecutionTime(self.logger, f"Workflow execution"):
                final_state = await self.graph.ainvoke(initial_state)
            
            # Calculate total processing time
            processing_time = time.time() - start_time
            final_state["processing_time"] = processing_time
            final_state["status"] = ProcessingStatus.COMPLETED
            
            # Build response
            response = self._build_response(final_state)
            
            self.logger.info(
                f"✅ Query processed successfully | "
                f"Intent: {final_state.get('intent', 'unknown')} | "
                f"Time: {processing_time:.2f}s | "
                f"Nodes: {len(final_state['nodes_visited'])}"
            )
            
            return response
            
        except Exception as e:
            self.logger.error(
                f"❌ Workflow execution failed: {str(e)}",
                exc_info=True
            )
            
            processing_time = time.time() - start_time
            
            # Return error response
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "processing_time": processing_time,
                "user_id": user_id,
                "query": query
            }
    
    def _build_response(self, state: GraphState) -> Dict[str, Any]:
        """
        Build final response from workflow state
        
        Args:
            state: Final workflow state
            
        Returns:
            Formatted response dictionary
        """
        intent = state.get("intent")
        
        # Base response
        response = {
            "success": True,
            "intent": intent.value if intent else "unknown",
            "processing_time": state.get("processing_time", 0),
            "nodes_visited": state.get("nodes_visited", []),
            "metadata": {
                "user_id": state["user_id"],
                "conversation_id": state.get("conversation_id"),
                "document_types_used": state.get("document_types_available", []),
                "num_documents_retrieved": len(state.get("retrieved_documents", []))
            }
        }
        
        # Add intent-specific data
        if state.get("generated_answer"):
            response["answer"] = state["generated_answer"]
        
        if state.get("evaluation_result"):
            response["evaluation"] = state["evaluation_result"]
        
        if state.get("final_response"):
            response["response"] = state["final_response"]
        
        if state.get("generated_questions"):
            response["questions"] = state["generated_questions"]
        
        # Add context info
        if state.get("context"):
            response["metadata"]["context_length"] = len(state["context"])
        
        return response
    
    def get_workflow_info(self) -> Dict[str, Any]:
        """
        Get information about the workflow structure
        
        Returns:
            Workflow metadata
        """
        return {
            "nodes": [
                "classify_intent",
                "retrieve_documents",
                "generate_answer",
                "evaluate_answer",
                "resolve_doubt",
                "generate_questions"
            ],
            "entry_point": "classify_intent",
            "supported_intents": [
                "answer_generation",
                "answer_evaluation",
                "doubt_clarification",
                "question_generation"
            ]
        }


# Global workflow instance
_workflow_instance = None


def get_workflow() -> WorkflowOrchestrator:
    """
    Get or create workflow singleton
    
    Returns:
        WorkflowOrchestrator instance
    """
    global _workflow_instance
    
    if _workflow_instance is None:
        _workflow_instance = WorkflowOrchestrator()
    
    return _workflow_instance


async def process_user_query(
    user_id: int,
    query: str,
    conversation_id: int = None
) -> Dict[str, Any]:
    """
    Convenience function to process a query
    
    Args:
        user_id: User ID
        query: User query
        conversation_id: Optional conversation ID
        
    Returns:
        Processing result
    """
    workflow = get_workflow()
    return await workflow.process_query(user_id, query, conversation_id)


if __name__ == "__main__":
    import asyncio
    
    async def test():
        # Initialize workflow
        workflow = get_workflow()
        
        # Print workflow info
        info = workflow.get_workflow_info()
        print("\n📊 Workflow Information:")
        print(f"Nodes: {info['nodes']}")
        print(f"Entry Point: {info['entry_point']}")
        print(f"Supported Intents: {info['supported_intents']}")
        
        # Test queries
        test_queries = [
            "What is machine learning?",
            "Generate answer for Q1 using marking scheme",
            "Evaluate my answer to this question",
            "Create 3 MCQs on neural networks"
        ]
        
        print("\n" + "="*60)
        print("TESTING WORKFLOW")
        print("="*60)
        
        for query in test_queries:
            print(f"\n📝 Query: {query}")
            
            try:
                result = await process_user_query(
                    user_id=1,
                    query=query
                )
                
                print(f"✅ Intent: {result['intent']}")
                print(f"⏱️  Time: {result['processing_time']:.2f}s")
                print(f"🔀 Nodes: {' → '.join(result['nodes_visited'])}")
                
                if result.get('response'):
                    print(f"📄 Response preview: {result['response'][:150]}...")
                
            except Exception as e:
                print(f"❌ Error: {str(e)}")
            
            print("-" * 60)
    
    asyncio.run(test())
