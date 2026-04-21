"""CLI Validator Agent for vEPC workflow."""
from typing import Dict, Any, List
from core.vepc_state import VEPCState
from core.vepc_base_agent import VEPCBaseAgent
from langchain_anthropic import ChatAnthropic
from config.vepc_settings import VEPC_ANTHROPIC_API_KEY, VEPC_ANTHROPIC_BASE_URL, VEPCSettings


class CLIValidatorAgent(VEPCBaseAgent):
    """Validates vEPC CLI command syntax."""

    def __init__(self):
        super().__init__("CLIValidator")
        self.llm = ChatAnthropic(
            model="claude-sonnet-4-6",
            api_key=VEPC_ANTHROPIC_API_KEY,
            base_url=VEPC_ANTHROPIC_BASE_URL,
            temperature=0.0,
        )
        self.settings = VEPCSettings()

    async def execute(self, state: VEPCState) -> VEPCState:
        """Validate CLI command syntax."""
        self._log("Validating CLI command syntax")

        commands = state.get("cli_commands", [])
        if not commands:
            return {
                **state,
                "validation_passed": True,
                "validation_errors": [],
                "validation_warnings": [],
            }

        # Validate each command
        errors = []
        warnings = []

        for cmd in commands:
            cmd_errors, cmd_warnings = await self._validate_command(cmd)
            errors.extend(cmd_errors)
            warnings.extend(cmd_warnings)

        validation_passed = len(errors) == 0

        if validation_passed:
            self._log("Validation passed")
        else:
            self._log(f"Validation failed with {len(errors)} error(s)", "warning")

        return {
            **state,
            "validation_passed": validation_passed,
            "validation_errors": errors,
            "validation_warnings": warnings,
        }

    async def _validate_command(self, command: str) -> tuple:
        """Validate a single CLI command."""
        cli_patterns = self.settings.get_cli_patterns()
        vepc_parameters = self.settings.get_vepc_parameters()

        prompt = f"""You are a vEPC CLI syntax validator.

Validate this CLI command for syntax correctness:
{command}

Valid CLI patterns:
{self._format_cli_patterns(cli_patterns)}

Known vEPC parameters:
{self._format_parameters(vepc_parameters)}

Check for:
1. Correct command structure (verb + parameter + value if needed)
2. Valid parameter names
3. Appropriate value format
4. Missing required arguments
5. Syntax errors

Respond in JSON format:
{{
    "valid": true/false,
    "errors": ["list of syntax errors if any"],
    "warnings": ["list of warnings if any"]
}}"""

        response = await self.llm.ainvoke(prompt)
        result = self._parse_response(response.content)

        return result.get("errors", []), result.get("warnings", [])

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

        # Fallback - assume valid if can't parse
        return {
            "valid": True,
            "errors": [],
            "warnings": ["Could not parse validation response"],
        }
