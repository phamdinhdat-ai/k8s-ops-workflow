"""Memory writer agent - persists session context and RCA findings."""
from typing import Dict, Any
from datetime import datetime
from core.base_agent import BaseAgent
from core.memory import MemoryStore


class MemoryWriterAgent(BaseAgent):
    """Writes session context and RCA findings to persistent memory."""
    
    def __init__(self, memory_store: MemoryStore):
        super().__init__("MemoryWriter")
        self.memory = memory_store
    
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Persist turn summary and RCA findings."""
        try:
            session_id = state.get("session_id")
            workflow_mode = state.get("workflow_mode")
            
            # Update session context
            user_context = state.get("user_context", {})
            if user_context.get("namespace"):
                self.memory.save_session_context(session_id, {
                    "preferred_namespace": user_context.get("namespace"),
                    "cluster_context": user_context.get("cluster"),
                    "last_query": state.get("user_query"),
                    "last_intent": state.get("intent"),
                    "history": state.get("conversation_history", [])
                })
            
            # Save RCA findings if in RCA mode
            if workflow_mode == "RCA" and state.get("root_cause"):
                root_cause = state.get("root_cause", {})
                impact = state.get("impact_assessment", {})
                
                rca_finding = {
                    "service": user_context.get("service_name"),
                    "namespace": user_context.get("namespace"),
                    "root_cause_summary": root_cause.get("primary_hypothesis", {}).get("description"),
                    "severity": impact.get("severity", "UNKNOWN"),
                    "remediation_applied": False,
                    "recurrence_count": 1
                }
                
                # Check for recurring incidents
                recent_rca = self.memory.get_recent_rca(
                    rca_finding["service"],
                    rca_finding["namespace"],
                    days=7
                )
                
                is_recurring = False
                previous_summary = None
                
                if recent_rca:
                    is_recurring = True
                    previous_summary = recent_rca.get("root_cause_summary")
                    rca_finding["recurrence_count"] = recent_rca.get("recurrence_count", 1) + 1
                    self._add_warning(state, f"Recurring incident detected. Previous: {previous_summary}")
                
                self.memory.save_rca_finding(rca_finding)
                
                result = {
                    "memory_written": True,
                    "is_recurring": is_recurring,
                    "previous_rca_summary": previous_summary
                }
            else:
                result = {
                    "memory_written": True,
                    "is_recurring": False,
                    "previous_rca_summary": None
                }
            
            self._add_response(state, result)
            
        except Exception as e:
            self._add_error(state, f"Memory write failed: {str(e)}")
        
        return state
