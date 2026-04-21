"""Knowledge Retriever Agent for vEPC workflow."""
from typing import Dict, Any, List
from core.vepc_state import VEPCState
from core.vepc_base_agent import VEPCBaseAgent
from config.vepc_settings import VEPC_VECTORDB_PATH, VEPC_VECTORDB_COLLECTION


class KnowledgeRetrieverAgent(VEPCBaseAgent):
    """Retrieves relevant vEPC documentation from vector database."""

    def __init__(self):
        super().__init__("KnowledgeRetriever")
        self.vectordb = None
        self._init_vectordb()

    def _init_vectordb(self):
        """Initialize ChromaDB connection."""
        try:
            import chromadb
            from chromadb.config import Settings

            client = chromadb.Client(
                Settings(
                    persist_directory=VEPC_VECTORDB_PATH,
                    anonymized_telemetry=False,
                )
            )
            self.vectordb = client.get_or_create_collection(
                name=VEPC_VECTORDB_COLLECTION
            )
            self._log("Vector database initialized")
        except Exception as e:
            self._log(f"Failed to initialize vector database: {e}", "error")

    async def execute(self, state: VEPCState) -> VEPCState:
        """Retrieve relevant knowledge from vector database."""
        self._log("Retrieving relevant knowledge")

        query = state.get("rewritten_query") or state["user_query"]
        intent = state.get("intent", "general")

        # Skip retrieval for general intents (greetings, thanks)
        if intent == "general":
            self._log("Skipping knowledge retrieval for general intent")
            return {
                **state,
                "knowledge_results": [],
                "knowledge_context": "",
            }

        # Retrieve from vector database
        results = self._retrieve(query, top_k=3)

        # Build context string
        context = self._build_context(results)

        self._log(f"Retrieved {len(results)} knowledge chunks")

        return {
            **state,
            "knowledge_results": results,
            "knowledge_context": context,
        }

    def _retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Retrieve top-k relevant documents."""
        if not self.vectordb:
            self._log("Vector database not available", "warning")
            return []

        try:
            results = self.vectordb.query(
                query_texts=[query],
                n_results=top_k,
            )

            # Format results
            documents = []
            if results and results.get("documents"):
                for i, doc in enumerate(results["documents"][0]):
                    metadata = results.get("metadatas", [[]])[0][i] if results.get("metadatas") else {}
                    documents.append({
                        "content": doc,
                        "metadata": metadata,
                        "relevance_score": 1.0 - (results.get("distances", [[]])[0][i] if results.get("distances") else 0),
                    })

            return documents
        except Exception as e:
            self._log(f"Retrieval failed: {e}", "error")
            return []

    def _build_context(self, results: List[Dict[str, Any]]) -> str:
        """Build context string from retrieved documents."""
        if not results:
            return ""

        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(f"[Document {i}]")
            context_parts.append(result["content"])
            context_parts.append("")

        return "\n".join(context_parts)
