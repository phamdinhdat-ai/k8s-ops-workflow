"""Response Synthesizer Agent for vEPC workflow."""
from typing import Dict, Any
from core.vepc_state import VEPCState
from core.vepc_base_agent import VEPCBaseAgent
from langchain_anthropic import ChatAnthropic
from config.vepc_settings import VEPC_ANTHROPIC_API_KEY, VEPC_ANTHROPIC_BASE_URL, VEPCSettings


class ResponseSynthesizerAgent(VEPCBaseAgent):
    """Synthesizes final response combining knowledge, CLI, and risk assessment."""

    def __init__(self):
        super().__init__("ResponseSynthesizer")
        self.llm = ChatAnthropic(
            model="claude-sonnet-4-6",
            api_key=VEPC_ANTHROPIC_API_KEY,
            base_url=VEPC_ANTHROPIC_BASE_URL,
            temperature=0.3,
        )
        self.settings = VEPCSettings()

    async def execute(self, state: VEPCState) -> VEPCState:
        """Synthesize final response."""
        self._log("Synthesizing final response")

        intent = state.get("intent")
        language = state.get("language", "en")
        query = state.get("rewritten_query") or state["user_query"]

        # Route to appropriate synthesis method
        if intent in ["show", "update"]:
            response = await self._synthesize_cli_response(state, language)
        elif intent in ["explain", "troubleshoot"]:
            response = await self._synthesize_knowledge_response(state, language)
        else:  # general
            response = await self._synthesize_general_response(state, language)

        self._log("Response synthesized")

        return {
            **state,
            "final_response": response,
            "response_metadata": {
                "intent": intent,
                "language": language,
                "has_cli": bool(state.get("cli_commands")),
                "risk_level": state.get("risk_level"),
            },
        }

    async def _synthesize_cli_response(self, state: VEPCState, language: str) -> str:
        """Synthesize response for CLI-based intents (show/update)."""
        commands = state.get("cli_commands", [])
        explanation = state.get("cli_explanation", "")
        knowledge_context = state.get("knowledge_context", "")
        risk_level = state.get("risk_level", "low")
        risk_warnings = state.get("risk_warnings", [])
        validation_warnings = state.get("validation_warnings", [])

        # Build CLI block
        cli_block = "\n".join(commands) if commands else "No command generated"

        # Get risk warning message
        risk_warning_msg = ""
        if risk_level in ["high", "critical"]:
            risk_warning_msg = self.settings.get_risk_warning(risk_level, language)
            if risk_warnings:
                risk_warning_msg += "\n" + "\n".join(f"- {w}" for w in risk_warnings)

        # Build validation warnings
        validation_msg = ""
        if validation_warnings:
            validation_msg = "\n\n⚠️ Warnings:\n" + "\n".join(f"- {w}" for w in validation_warnings)

        prompt = f"""You are a vEPC assistant. Generate a clear, helpful response.

User query: {state.get('user_query')}
Language: {language}

CLI command(s):
```
{cli_block}
```

Explanation: {explanation}

Risk level: {risk_level}
{risk_warning_msg}

{validation_msg}

Additional context from documentation:
{knowledge_context[:300] if knowledge_context else "None"}

Generate a response that:
1. Presents the CLI command clearly
2. Explains what it does
3. Includes risk warnings if applicable
4. Is in {language} language
5. Is concise and professional

Response:"""

        response = await self.llm.ainvoke(prompt)
        return response.content

    async def _synthesize_knowledge_response(self, state: VEPCState, language: str) -> str:
        """Synthesize response for knowledge-based intents (explain/troubleshoot)."""
        knowledge_context = state.get("knowledge_context", "")
        query = state.get("rewritten_query") or state["user_query"]

        prompt = f"""You are a vEPC assistant. Answer the user's question using the provided documentation.

User query: {query}
Language: {language}

Documentation context:
{knowledge_context}

Generate a response that:
1. Directly answers the question
2. Uses information from the documentation
3. Is clear and concise
4. Is in {language} language
5. Includes examples if helpful

If the documentation doesn't contain enough information, acknowledge that and provide what you can.

Response:"""

        response = await self.llm.ainvoke(prompt)
        return response.content

    async def _synthesize_general_response(self, state: VEPCState, language: str) -> str:
        """Synthesize response for general intents (greetings, thanks)."""
        query = state.get("user_query", "")

        # Simple template-based responses for common patterns
        query_lower = query.lower()

        if language == "vi":
            if any(word in query_lower for word in ["xin chào", "chào", "hello", "hi"]):
                return "Xin chào! Tôi là trợ lý vEPC. Tôi có thể giúp bạn:\n- Xem cấu hình hiện tại\n- Thay đổi cấu hình\n- Giải thích các khái niệm vEPC\n- Hỗ trợ khắc phục sự cố\n\nBạn cần giúp gì?"
            elif any(word in query_lower for word in ["cảm ơn", "thanks", "thank"]):
                return "Không có gì! Nếu bạn cần thêm trợ giúp, cứ hỏi nhé."
        else:
            if any(word in query_lower for word in ["hello", "hi", "hey"]):
                return "Hello! I'm a vEPC assistant. I can help you:\n- View current configuration\n- Modify configuration\n- Explain vEPC concepts\n- Troubleshoot issues\n\nWhat can I help you with?"
            elif any(word in query_lower for word in ["thanks", "thank"]):
                return "You're welcome! Let me know if you need anything else."

        # Fallback
        return "I'm here to help with vEPC operations. You can ask me to show configuration, make changes, explain concepts, or troubleshoot issues."
