"""Response validator agent - validates response quality."""
from typing import Dict, Any
from core.base_agent import BaseAgent


class ResponseValidatorAgent(BaseAgent):
    """Validates response quality and detects hallucinations."""
    
    def __init__(self):
        super().__init__("ResponseValidator")
    
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Validate response data quality."""
        try:
            validation_result = {
                "valid": True,
                "issues": [],
                "retry": False
            }
            
            # Check K8s state if present
            k8s_state = state.get("k8s_state")
            if k8s_state is not None:
                if not k8s_state or k8s_state == {}:
                    validation_result["valid"] = False
                    validation_result["issues"].append("Empty K8s state returned")
                    validation_result["retry"] = True
                
                # Check for error strings in response
                if isinstance(k8s_state, dict) and "error" in str(k8s_state).lower():
                    validation_result["valid"] = False
                    validation_result["issues"].append("Error detected in K8s response")
                
                # Validate resource names match intent entities
                intent_entities = state.get("intent_entities", {})
                if intent_entities.get("service_name"):
                    expected_name = intent_entities["service_name"]
                    response_str = str(k8s_state)
                    if expected_name not in response_str:
                        self._add_warning(state, f"Expected service '{expected_name}' not found in response")
            
            # Check knowledge results if present
            knowledge_results = state.get("knowledge_results", [])
            if state.get("intent") == "QUERY_KNOWLEDGE" and not knowledge_results:
                validation_result["valid"] = False
                validation_result["issues"].append("No knowledge results returned")
            
            # Check report if present
            report = state.get("report")
            if report is not None:
                if not report or len(str(report)) < 50:
                    validation_result["valid"] = False
                    validation_result["issues"].append("Report too short or empty")
            
            state["validation_result"] = validation_result
            
            if not validation_result["valid"]:
                for issue in validation_result["issues"]:
                    self._add_warning(state, issue)
            
            self._add_response(state, validation_result)
            
        except Exception as e:
            self._add_error(state, f"Validation failed: {str(e)}")
            state["validation_result"] = {"valid": False, "issues": [str(e)], "retry": False}
        
        return state
