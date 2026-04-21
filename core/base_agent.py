"""Base agent class for all workflow agents."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from anthropic import Anthropic
import os


class BaseAgent(ABC):
    """Base class for all agents in the workflow."""
    
    def __init__(self, name: str, llm: Optional[Anthropic] = None):
        self.name = name
        self.llm = llm or Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            base_url=os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com")
        )
    
    @abstractmethod
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent logic and return updated state."""
        pass
    
    def _add_response(self, state: Dict[str, Any], result: Dict[str, Any]):
        """Add agent response to state tracking."""
        state["agent_responses"].append({
            "agent": self.name,
            "result": result,
            "phase": state.get("current_phase", "unknown")
        })
    
    def _add_error(self, state: Dict[str, Any], error: str):
        """Add error to state."""
        state["errors"].append(f"[{self.name}] {error}")
    
    def _add_warning(self, state: Dict[str, Any], warning: str):
        """Add warning to state."""
        state["warnings"].append(f"[{self.name}] {warning}")
