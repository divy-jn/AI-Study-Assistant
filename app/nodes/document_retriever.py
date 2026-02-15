"""
Document Retrieval Node
Retrieves relevant document chunks based on user query and intent
"""
from typing import List, Dict, Any, Optional
from app.core.state import GraphState, Intent, RetrievedDocument

from app.core.logging_config import get_logger, LogExecutionTime
from app.services.vector_store_service import get_vector_store
from app.core.exceptions import WorkflowNodeException
from app.core.config import settings


logger = get_logger(__name__)


class DocumentRetriever:
    """
    Retrieves relevant documents from vector store based on query and intent
    """
    
    # Number of documents to retrieve per intent
    RETRIEVAL_COUNTS = {
        Intent.ANSWER_GENERATION: 10,
        Intent.ANSWER_EVALUATION: 5,  # Mainly marking scheme
        Intent.DOUBT_CLARIFICATION: 8,
        Intent.QUESTION_GENERATION: 10,
        Intent.EXAM_PAPER_GENERATION: 15,
    }
    
    # Document type priorities per intent
    DOCUMENT_TYPE_PRIORITIES = {
        Intent.ANSWER_GENERATION: ["marking_scheme", "notes", "question_paper"],
        Intent.ANSWER_EVALUATION: ["marking_scheme"],
        Intent.DOUBT_CLARIFICATION: ["notes", "marking_scheme"],
        Intent.QUESTION_GENERATION: ["notes", "question_paper"],
        Intent.EXAM_PAPER_GENERATION: ["notes", "question_paper", "marking_scheme"],
    }
    
    def __init__(self):
        self.logger = logger
        self.vector_store = None
    
    async def retrieve(self, state: GraphState) -> GraphState:
        """
        Retrieve relevant documents
        
        Args:
            state: Current graph state
            
        Returns:
            Updated state with retrieved documents
        """
        query = state["query"]
        intent = state.get("intent", Intent.DOUBT_CLARIFICATION)
        user_id = state["user_id"]
        
        self.logger.info(
            f"🔍 Retrieving documents | "
            f"Intent: {intent.value} | "
            f"Query: '{query[:100]}'"
        )
        
        with LogExecutionTime(self.logger, "Document retrieval"):
            try:
                # Initialize vector store if needed
                if self.vector_store is None:
                    self.vector_store = get_vector_store()
                
                # Build enhanced query based on intent
                enhanced_query = self._enhance_query(query, intent)
                
                # Determine how many documents to retrieve
                n_results = self.RETRIEVAL_COUNTS.get(intent, 10)
                
                # Perform semantic search
                search_results = self.vector_store.search(
                    query=enhanced_query,
                    n_results=n_results * 2,  # Retrieve more, then filter
                    include=["documents", "metadatas", "distances"]
                )
                
                # Filter and rank results
                filtered_results = self._filter_and_rank_results(
                    search_results,
                    intent,
                    user_id,
                    n_results
                )
                
                # Convert to RetrievedDocument format
                retrieved_docs = self._format_retrieved_documents(filtered_results)
                
                # Build context string
                context = self._build_context(retrieved_docs)
                
                # Get available document types
                doc_types = list(set(doc["document_type"] for doc in retrieved_docs))
                
                # Update state
                state["retrieved_documents"] = retrieved_docs
                state["context"] = context
                state["document_types_available"] = doc_types
                state["retrieval_query"] = enhanced_query
                state["nodes_visited"].append("document_retriever")
                
                self.logger.info(
                    f"✅ Retrieved {len(retrieved_docs)} documents | "
                    f"Types: {doc_types} | "
                    f"Context length: {len(context)} chars"
                )
                
                return state
                
            except Exception as e:
                self.logger.error(f"❌ Document retrieval failed: {str(e)}", exc_info=True)
                
                # Set empty results instead of failing
                state["retrieved_documents"] = []
                state["context"] = ""
                state["document_types_available"] = []
                state["nodes_visited"].append("document_retriever")
                
                self.logger.warning("⚠️ Continuing with empty document set")
                
                return state
    
    def _enhance_query(self, query: str, intent: Intent) -> str:
        """
        Enhance query with intent-specific context
        
        Args:
            query: Original query
            intent: Classified intent
            
        Returns:
            Enhanced query string
        """
        # Add intent-specific keywords to improve retrieval
        enhancements = {
            Intent.ANSWER_GENERATION: "answer solution explanation",
            Intent.ANSWER_EVALUATION: "marking scheme grading criteria",
            Intent.DOUBT_CLARIFICATION: "explanation concept definition",
            Intent.QUESTION_GENERATION: "questions examples problems",
            Intent.EXAM_PAPER_GENERATION: "questions topics syllabus",
        }
        
        enhancement = enhancements.get(intent, "")
        return f"{query} {enhancement}".strip()
    
    def _filter_and_rank_results(
        self,
        search_results: Dict[str, Any],
        intent: Intent,
        user_id: int,
        n_results: int
    ) -> List[Dict[str, Any]]:
        """
        Filter and rank search results based on intent and user access
        
        Args:
            search_results: Raw search results from vector store
            intent: User intent
            user_id: User ID for access control
            n_results: Number of results to return
            
        Returns:
            Filtered and ranked results
        """
        results = search_results.get("results", [])
        
        if not results:
            return []
        
        # Get document type priorities for this intent
        type_priorities = self.DOCUMENT_TYPE_PRIORITIES.get(intent, [])
        
        # Score and filter results
        scored_results = []
        for result in results:
            metadata = result.get("metadata", {})
            
            # Check access (user's own docs or public docs)
            if metadata.get("user_id") != user_id and metadata.get("visibility") != "public":
                continue
            
            # Base score from similarity
            score = result.get("similarity", 0.0)
            
            # Boost score based on document type priority
            doc_type = metadata.get("document_type", "other")
            if doc_type in type_priorities:
                priority_index = type_priorities.index(doc_type)
                boost = (len(type_priorities) - priority_index) * 0.1
                score += boost
            
            # Filter by similarity threshold
            if score >= settings.SIMILARITY_THRESHOLD:
                scored_results.append({
                    "result": result,
                    "score": score
                })
        
        # Sort by score (descending)
        scored_results.sort(key=lambda x: x["score"], reverse=True)
        
        # Return top n results
        return [item["result"] for item in scored_results[:n_results]]
    
    def _format_retrieved_documents(
        self,
        results: List[Dict[str, Any]]
    ) -> List[RetrievedDocument]:
        """
        Convert raw results to RetrievedDocument format
        
        Args:
            results: Filtered search results
            
        Returns:
            List of RetrievedDocument dicts
        """
        retrieved_docs = []
        
        for result in results:
            metadata = result.get("metadata", {})
            
            doc = RetrievedDocument(
                document_id=metadata.get("document_id", 0),
                document_type=metadata.get("document_type", "other"),
                chunk_text=result.get("document", ""),
                similarity_score=result.get("similarity", 0.0),
                metadata=metadata
            )
            
            retrieved_docs.append(doc)
        
        return retrieved_docs
    
    def _build_context(self, documents: List[RetrievedDocument]) -> str:
        """
        Build context string from retrieved documents
        
        Args:
            documents: Retrieved documents
            
        Returns:
            Formatted context string
        """
        if not documents:
            return ""
        
        context_parts = []
        
        # Group by document type
        by_type: Dict[str, List[RetrievedDocument]] = {}
        for doc in documents:
            doc_type = doc["document_type"]
            if doc_type not in by_type:
                by_type[doc_type] = []
            by_type[doc_type].append(doc)
        
        # Format each group
        for doc_type, docs in by_type.items():
            context_parts.append(f"\n--- {doc_type.upper().replace('_', ' ')} ---\n")
            
            for i, doc in enumerate(docs, 1):
                # Add chunk with metadata
                chunk_info = f"[Chunk {i} | Similarity: {doc['similarity_score']:.2f}]"
                context_parts.append(f"{chunk_info}\n{doc['chunk_text']}\n")
        
        return "\n".join(context_parts)
    
    async def retrieve_by_document_type(
        self,
        state: GraphState,
        document_types: List[str],
        n_results: int = 10
    ) -> List[RetrievedDocument]:
        """
        Retrieve documents of specific types
        
        Args:
            state: Current graph state
            document_types: List of document types to retrieve
            n_results: Number of results per type
            
        Returns:
            Retrieved documents
        """
        if self.vector_store is None:
            self.vector_store = get_vector_store()
        
        all_results = []
        
        for doc_type in document_types:
            # Search with document type filter
            results = self.vector_store.search(
                query=state["query"],
                n_results=n_results,
                where={"document_type": doc_type}
            )
            
            formatted = self._format_retrieved_documents(results.get("results", []))
            all_results.extend(formatted)
        
        return all_results


# Global instance
_document_retriever = DocumentRetriever()


async def retrieve_documents_node(state: GraphState) -> GraphState:
    """
    LangGraph node function for document retrieval
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with retrieved documents
    """
    return await _document_retriever.retrieve(state)


if __name__ == "__main__":
    import asyncio
    from langgraph_state import create_initial_state, Intent
    from vector_store_service import get_vector_store
    
    async def test():
        # Setup: Add some test documents to vector store
        vector_store = get_vector_store()
        
        test_docs = [
            "Machine learning is a subset of AI that focuses on learning from data.",
            "Marking Scheme Q1: Definition of ML (2 marks), Examples (3 marks)",
            "Neural networks are inspired by biological neurons in the brain."
        ]
        
        test_metadata = [
            {"document_type": "notes", "user_id": 1, "visibility": "public"},
            {"document_type": "marking_scheme", "user_id": 1, "visibility": "public"},
            {"document_type": "notes", "user_id": 1, "visibility": "public"},
        ]
        
        vector_store.add_documents(test_docs, test_metadata)
        
        # Test retrieval
        state = create_initial_state(
            user_id=1,
            query="Explain machine learning with examples"
        )
        state["intent"] = Intent.DOUBT_CLARIFICATION
        
        result = await retrieve_documents_node(state)
        
        print(f"\n📚 Retrieved {len(result['retrieved_documents'])} documents")
        print(f"📝 Document types: {result['document_types_available']}")
        print(f"\n🔍 Context preview:\n{result['context'][:500]}...")
    
    asyncio.run(test())
