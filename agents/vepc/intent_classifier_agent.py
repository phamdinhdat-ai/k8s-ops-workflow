"""Intent Classifier Agent for vEPC workflow."""
from typing import Dict, Any
from core.vepc_state import VEPCState
from core.vepc_base_agent import VEPCBaseAgent
from langchain_anthropic import ChatAnthropic
from config.vepc_settings import VEPC_ANTHROPIC_API_KEY, VEPC_ANTHROPIC_BASE_URL, VEPCSettings


class IntentClassifierAgent(VEPCBaseAgent):
    """Classifies user intent: show/update/explain/troubleshoot/general."""

    def __init__(self):
        super().__init__("IntentClassifier")
        self.llm = ChatAnthropic(
            model="claude-sonnet-4-6",
            api_key=VEPC_ANTHROPIC_API_KEY,
            base_url=VEPC_ANTHROPIC_BASE_URL,
            temperature=0.1,
        )
        self.settings = VEPCSettings()

    async def execute(self, state: VEPCState) -> VEPCState:
        """Classify the intent of the user query."""
        self._log("Classifying user intent")

        query = state.get("rewritten_query") or state["user_query"]
        language = state.get("language", "en")

        # Get intent examples from config
        intent_examples = self.settings.get_intent_examples()

        prompt = f"""You are an intent classifier for a vEPC (virtual Evolved Packet Core) assistant.

Classify the user's query into one of these intents:
- **show**: User wants to view/display current configuration or status (read-only)
- **update**: User wants to change/modify configuration (write operation)
- **explain**: User wants to understand a concept, parameter, or feature
- **troubleshoot**: User needs help diagnosing or fixing an issue
- **general**: Greetings, thanks, or general conversation

User query: {query}
Language: {language}

Intent examples:
{self._format_examples(intent_examples)}

Extract any entities mentioned (parameters, values, components).

Respond in JSON format:
{{
    "intent": "show|update|explain|troubleshoot|general",
    "confidence": 0.0-1.0,
    "entities": {{
        "parameter": "extracted parameter name if any",
        "value": "extracted value if any",
        "component": "vEPC component if any"
    }},
    "reasoning": "brief explanation of classification"
}}"""

        response = await self.llm.ainvoke(prompt)
        result = self._parse_response(response.content)

        self._log(f"Intent: {result['intent']} (confidence: {result['confidence']})")

        return {
            **state,
            "intent": result["intent"],
            "intent_confidence": result["confidence"],
            "intent_entities": result["entities"],
            "intent_reasoning": result["reasoning"],
        }

    def _format_examples(self, examples: Dict[str, Dict[str, list]]) -> str:
        """Format intent examples for prompt."""
        lines = []
        for intent, lang_examples in examples.items():
            lines.append(f"\n{intent.upper()}:")
            for lang, queries in lang_examples.items():
                for query in queries[:2]:  # Show 2 examples per language
                    lines.append(f"  - {query}")
        return "\n".join(lines)

    def _parse_response(self, content: str) -> Dict[str, Any]:
        """Parse LLM response."""
        import json
        try:
            start = content.find("{")
            end = content.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(content[start:end])
        except:
            pass

        # Fallback
        return {
            "intent": "general",
            "confidence": 0.5,
            "entities": {},
            "reasoning": "Failed to parse response",
        }
