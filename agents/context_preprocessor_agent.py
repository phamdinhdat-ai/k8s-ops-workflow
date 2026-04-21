"""Context preprocessor agent - normalizes context before intent classification."""
import re
from typing import Dict, Any
from core.base_agent import BaseAgent
from core.memory import MemoryStore


class ContextPreProcessorAgent(BaseAgent):
    """Enriches user_context from memory, history, and query text."""
    
    def __init__(self, memory_store: MemoryStore):
        super().__init__("ContextPreProcessor")
        self.memory = memory_store
    
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize and enrich context before intent classification."""
        try:
            user_context = state.get("user_context", {})
            session_id = state.get("session_id")
            query = state.get("user_query", "")
            
            # Load memory context
            memory_ctx = self.memory.get_session_context(session_id)
            if memory_ctx:
                user_context.setdefault("namespace", memory_ctx.get("preferred_namespace"))
                user_context.setdefault("cluster", memory_ctx.get("cluster_context"))
            
            # Extract from conversation history
            history = state.get("conversation_history", [])
            for turn in history[-3:]:
                if "namespace" in turn.get("content", "").lower():
                    ns_match = re.search(r'namespace[:\s]+(\S+)', turn["content"])
                    if ns_match:
                        user_context.setdefault("namespace", ns_match.group(1))
            
            # Extract from query text
            patterns = {
                "namespace": r'(?:namespace|ns)[:\s/]+(\S+)',
                "service": r'(?:service|svc)[:\s/]+(\S+)',
                "pod": r'(?:pod)[:\s/]+(\S+)',
            }
            
            for key, pattern in patterns.items():
                if key not in user_context or not user_context[key]:
                    match = re.search(pattern, query, re.IGNORECASE)
                    if match:
                        user_context[key] = match.group(1)
            
            # Common namespace aliases
            if "prod" in query.lower() and not user_context.get("namespace"):
                user_context["namespace"] = "production"
            elif "staging" in query.lower() and not user_context.get("namespace"):
                user_context["namespace"] = "staging"
            
            state["user_context"] = user_context
            state["memory_context"] = memory_ctx
            state["context_enriched"] = bool(user_context.get("namespace"))
            
            self._add_response(state, {
                "enriched_context": user_context,
                "from_memory": bool(memory_ctx),
                "from_query": any(re.search(p, query, re.IGNORECASE) for p in patterns.values())
            })
            
        except Exception as e:
            self._add_error(state, f"Context preprocessing failed: {str(e)}")
        
        return state
