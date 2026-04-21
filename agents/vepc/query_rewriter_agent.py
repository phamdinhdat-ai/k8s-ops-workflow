"""Query Rewriter Agent for vEPC workflow."""
from typing import Dict, Any
from core.vepc_state import VEPCState
from core.vepc_base_agent import VEPCBaseAgent
from langchain_anthropic import ChatAnthropic
from config.vepc_settings import VEPC_ANTHROPIC_API_KEY, VEPC_ANTHROPIC_BASE_URL


class QueryRewriterAgent(VEPCBaseAgent):
    """Rewrites ambiguous or follow-up queries using conversation context."""

    def __init__(self):
        super().__init__("QueryRewriter")
        self.llm = ChatAnthropic(
            model="claude-sonnet-4-6",
            api_key=VEPC_ANTHROPIC_API_KEY,
            base_url=VEPC_ANTHROPIC_BASE_URL,
            temperature=0.3,
        )

    async def execute(self, state: VEPCState) -> VEPCState:
        """Rewrite query if needed based on conversation history."""
        self._log("Analyzing query for rewriting needs")

        user_query = state["user_query"]
        conversation_history = state.get("conversation_history", [])

        # If no history or query is already clear, skip rewriting
        if not conversation_history or self._is_standalone_query(user_query):
            self._log("Query is standalone, no rewriting needed")
            return {
                **state,
                "rewritten_query": user_query,
                "rewrite_reasoning": "Query is already clear and standalone",
            }

        # Build context from conversation history
        context = self._build_context(conversation_history)

        # Rewrite query
        prompt = f"""You are a query rewriter for a vEPC (virtual Evolved Packet Core) assistant.

Given the conversation history and the current user query, rewrite the query to be standalone and unambiguous.

Conversation history:
{context}

Current query: {user_query}

If the query references previous context (e.g., "change it to 90", "what about that timer?"), expand it to be fully explicit.
If the query is already clear, return it unchanged.

Respond in JSON format:
{{
    "rewritten_query": "the rewritten query",
    "reasoning": "why you rewrote it this way or why no rewrite was needed"
}}"""

        response = await self.llm.ainvoke(prompt)
        result = self._parse_response(response.content)

        self._log(f"Rewritten query: {result['rewritten_query']}")

        return {
            **state,
            "rewritten_query": result["rewritten_query"],
            "rewrite_reasoning": result["reasoning"],
        }

    def _is_standalone_query(self, query: str) -> bool:
        """Check if query is standalone (doesn't need context)."""
        ambiguous_patterns = ["it", "that", "this", "them", "those", "same", "also"]
        query_lower = query.lower()
        return not any(pattern in query_lower for pattern in ambiguous_patterns)

    def _build_context(self, history: list) -> str:
        """Build context string from conversation history."""
        context_lines = []
        for turn in history[-3:]:  # Last 3 turns
            context_lines.append(f"User: {turn.get('user', '')}")
            context_lines.append(f"Assistant: {turn.get('assistant', '')}")
        return "\n".join(context_lines)

    def _parse_response(self, content: str) -> Dict[str, str]:
        """Parse LLM response."""
        import json
        try:
            # Try to extract JSON from response
            start = content.find("{")
            end = content.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(content[start:end])
        except:
            pass

        # Fallback
        return {
            "rewritten_query": content,
            "reasoning": "Failed to parse structured response",
        }
