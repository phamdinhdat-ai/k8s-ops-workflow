"""Risk Assessor Agent for vEPC workflow."""
from typing import Dict, Any, List
from core.vepc_state import VEPCState
from core.vepc_base_agent import VEPCBaseAgent
from langchain_anthropic import ChatAnthropic
from config.vepc_settings import VEPC_ANTHROPIC_API_KEY, VEPC_ANTHROPIC_BASE_URL, VEPCSettings


class RiskAssessorAgent(VEPCBaseAgent):
    """Assesses risk level of vEPC configuration changes."""

    def __init__(self):
        super().__init__("RiskAssessor")
        self.llm = ChatAnthropic(
            model="claude-sonnet-4-6",
            api_key=VEPC_ANTHROPIC_API_KEY,
            base_url=VEPC_ANTHROPIC_BASE_URL,
            temperature=0.1,
        )
        self.settings = VEPCSettings()

    async def execute(self, state: VEPCState) -> VEPCState:
        """Assess risk level of CLI commands."""
        self._log("Assessing risk level")

        intent = state.get("intent")
        commands = state.get("cli_commands", [])

        # Skip risk assessment for read-only operations
        if intent in ["show", "explain", "troubleshoot", "general"]:
            self._log("Skipping risk assessment for read-only intent")
            return {
                **state,
                "risk_level": "low",
                "risk_warnings": [],
                "impact_description": "Read-only operation with no impact",
                "affected_components": [],
            }

        if not commands:
            return {
                **state,
                "risk_level": "low",
                "risk_warnings": [],
                "impact_description": "No commands to assess",
                "affected_components": [],
            }

        # Assess risk for each command
        risk_levels = self.settings.get_risk_levels()

        risk_results = []
        for cmd in commands:
            result = await self._assess_command(cmd, risk_levels)
            risk_results.append(result)

        # Aggregate risk (take highest)
        overall_risk = self._aggregate_risk([r["risk_level"] for r in risk_results])
        all_warnings = []
        all_affected = []

        for result in risk_results:
            all_warnings.extend(result["warnings"])
            all_affected.extend(result["affected_components"])

        impact_description = self._build_impact_description(risk_results)

        self._log(f"Risk level: {overall_risk}")

        return {
            **state,
            "risk_level": overall_risk,
            "risk_warnings": all_warnings,
            "impact_description": impact_description,
            "affected_components": list(set(all_affected)),
        }

    async def _assess_command(self, command: str, risk_levels: Dict[str, Dict]) -> Dict[str, Any]:
        """Assess risk for a single command."""
        prompt = f"""You are a vEPC risk assessor.

Analyze this CLI command for operational risk:
{command}

Risk level definitions:
{self._format_risk_levels(risk_levels)}

Assess:
1. What components/services could be affected?
2. Could this cause service outage or session drops?
3. Is this reversible?
4. What's the blast radius?

Respond in JSON format:
{{
    "risk_level": "low|medium|high|critical",
    "warnings": ["specific warnings about this command"],
    "affected_components": ["list of affected vEPC components"],
    "impact_description": "brief description of potential impact",
    "reversible": true/false
}}"""

        response = await self.llm.ainvoke(prompt)
        result = self._parse_response(response.content)

        return result

    def _format_risk_levels(self, risk_levels: Dict[str, Dict]) -> str:
        """Format risk level definitions for prompt."""
        lines = []
        for level, definition in risk_levels.items():
            lines.append(f"{level.upper()}: {definition.get('description', '')}")
            if definition.get('keywords'):
                lines.append(f"  Keywords: {', '.join(definition['keywords'])}")
            if definition.get('parameters'):
                lines.append(f"  Parameters: {', '.join(definition['parameters'])}")
        return "\n".join(lines)

    def _aggregate_risk(self, risk_levels: List[str]) -> str:
        """Aggregate multiple risk levels to overall risk."""
        risk_order = ["low", "medium", "high", "critical"]
        max_risk = "low"

        for risk in risk_levels:
            if risk in risk_order:
                if risk_order.index(risk) > risk_order.index(max_risk):
                    max_risk = risk

        return max_risk

    def _build_impact_description(self, risk_results: List[Dict]) -> str:
        """Build overall impact description."""
        descriptions = [r.get("impact_description", "") for r in risk_results if r.get("impact_description")]
        return " ".join(descriptions) if descriptions else "Configuration change with potential impact"

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

        # Fallback - assume medium risk if can't parse
        return {
            "risk_level": "medium",
            "warnings": ["Could not parse risk assessment"],
            "affected_components": [],
            "impact_description": "Unknown impact",
            "reversible": True,
        }
