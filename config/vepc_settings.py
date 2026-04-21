"""vEPC-specific settings and configuration loader."""
import os
import yaml
from pathlib import Path
from typing import Dict, Any, List


class VEPCSettings:
    """Configuration manager for vEPC workflow."""

    def __init__(self):
        self.config_dir = Path(__file__).parent / "vepc"
        self.templates = self._load_templates()

    def _load_templates(self) -> Dict[str, Any]:
        """Load vEPC templates from YAML."""
        template_path = self.config_dir / "templates.yaml"
        if template_path.exists():
            with open(template_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        return {}

    def get_cli_patterns(self) -> Dict[str, List[str]]:
        """Get CLI command patterns."""
        return self.templates.get("cli_patterns", {})

    def get_risk_levels(self) -> Dict[str, Dict[str, Any]]:
        """Get risk assessment rules."""
        return self.templates.get("risk_levels", {})

    def get_vepc_parameters(self) -> Dict[str, List[str]]:
        """Get known vEPC parameters."""
        return self.templates.get("vepc_parameters", {})

    def get_intent_examples(self) -> Dict[str, Dict[str, List[str]]]:
        """Get intent classification examples."""
        return self.templates.get("intent_examples", {})

    def get_response_templates(self) -> Dict[str, Any]:
        """Get response templates."""
        return self.templates.get("response_templates", {})

    def get_risk_warning(self, risk_level: str, language: str = "en") -> str:
        """Get risk warning message for given level and language."""
        warnings = self.templates.get("response_templates", {}).get("risk_warning", {})
        return warnings.get(risk_level, {}).get(language, "")


# Environment variables for vEPC
VEPC_ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
VEPC_ANTHROPIC_BASE_URL = os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com")
VEPC_VECTORDB_PATH = os.getenv("VEPC_VECTORDB_PATH", "./data/vepc_vectordb")
VEPC_VECTORDB_COLLECTION = os.getenv("VEPC_VECTORDB_COLLECTION", "vepc_docs")
VEPC_MAX_VALIDATION_RETRIES = int(os.getenv("VEPC_MAX_VALIDATION_RETRIES", "2"))
VEPC_CLI_TIMEOUT = int(os.getenv("VEPC_CLI_TIMEOUT", "30"))
VEPC_STREAMING_ENABLED = os.getenv("VEPC_STREAMING_ENABLED", "true").lower() == "true"
VEPC_DEBUG_MODE = os.getenv("VEPC_DEBUG_MODE", "false").lower() == "true"
