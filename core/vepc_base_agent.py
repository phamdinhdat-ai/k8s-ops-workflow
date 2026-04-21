"""Base agent class for vEPC workflow agents."""
from abc import ABC, abstractmethod
from typing import Dict, Any
from core.vepc_state import VEPCState


class VEPCBaseAgent(ABC):
    """Base class for all vEPC agents."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def execute(self, state: VEPCState) -> VEPCState:
        """
        Execute the agent's logic.

        Args:
            state: Current workflow state

        Returns:
            Updated workflow state
        """
        pass

    def _log(self, message: str, level: str = "info"):
        """Log agent activity."""
        print(f"[{self.name}] [{level.upper()}] {message}")
