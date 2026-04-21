"""CLI Generator Agent for vEPC workflow."""
from typing import Dict, Any, List
from core.vepc_state import VEPCState
from core.vepc_base_agent import VEPCBaseAgent
from langchain_anthropic import ChatAnthropic
from config.vepc_settings import VEPC_ANTHROPIC_API_KEY, VEPC_ANTHROPIC_BASE_URL, VEPCSettings


class CLIGeneratorAgent(VEPCBaseAgent):
    """Generates vEPC CLI commands from user intent."""

    def __init__(self):
        super().__init__("CLIGenerator")
        self.llm = ChatAnthropic(
            model="claude-sonnet-4-6",
            api_key=VEPC_ANTHROPIC_API_KEY,
            base_url=VEPC_ANTHROPIC_BASE_URL,
            temperature=0.2,
        )
        self.settings = VEPCSettings()

    async def execute(self, state: VEPCState) -> VEPCState:
        """Generate CLI command(s) based on intent and entities."""
        self._log("Generating CLI command")

        intent = state.get("intent")
        entities = state.get("intent_entities", {})
        query = state.get("rewritten_query") or state["user_query"]
        knowledge_context = state.get("knowledge_context", "")
        language = state.get("language", "en")

        # Get CLI patterns and parameters
        cli_patterns = self.settings.get_cli_patterns()
        vepc_parameters = self.settings.get_vepc_parameters()

        prompt = f"""You are a vEPC CLI command generator.

User intent: {intent}
User query: {query}
Extracted entities: {entities}
Language: {language}

Available CLI patterns:
{self._format_cli_patterns(cli_patterns)}

Known vEPC parameters:
{self._format_parameters(vepc_parameters)}

Knowledge context:
{knowledge_context[:500] if knowledge_context else "No additional context"}

Generate the correct vEPC CLI command(s) to fulfill the user's request.

Rules:
1. Use exact parameter names from the known parameters list
2. Follow the CLI patterns for the intent type
3. If multiple commands are needed, provide them as a list
4. Ensure syntax is correct and complete
5. Include units where applicable (e.g., "60 minutes" for timers)

Respond in JSON format:
{{
    "commands": ["command1", "command2"],
    "explanation": "brief explanation of what these commands do",
    "reasoning": "why you chose this approach"
}}"""

        response = await self.llm.ainvoke(prompt)
        result = self._parse_response(response.content)

        self._log(f"Generated {len(result['commands'])} command(s)")

        return {
            **state,
            "cli_commands": result["commands"],
            "cli_explanation": result["explanation"],
            "cli_generation_reasoning": result["reasoning"],
        }

    def _format_cli_patterns(self, patterns: Dict[str, List[str]]) -> str:
        """Format CLI patterns for prompt."""
        lines = []
        for intent_type, pattern_list in patterns.items():
            lines.append(f"{intent_type}:")
            for pattern in pattern_list:
                lines.append(f"  - {pattern}")
        return "\n".join(lines)

    def _format_parameters(self, parameters: Dict[str, List[str]]) -> str:
        """Format vEPC parameters for prompt."""
        lines = []
        for category, param_list in parameters.items():
            lines.append(f"{category}: {', '.join(param_list)}")
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
            "commands": [content.strip()],
            "explanation": "Generated command",
            "reasoning": "Failed to parse structured response",
        }
