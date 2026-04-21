"""Impact assessor agent - assesses blast radius and severity."""
from typing import Dict, Any
from core.base_agent import BaseAgent


class ImpactAssessorAgent(BaseAgent):
    """Assesses incident impact and severity."""
    
    def __init__(self):
        super().__init__("ImpactAssessor")
    
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Assess impact and classify severity."""
        try:
            user_context = state.get("user_context", {})
            k8s_state = state.get("k8s_state", {})
            detected_problems = state.get("detected_problems", [])
            root_cause = state.get("root_cause", {})
            
            service_name = user_context.get("service_name")
            namespace = user_context.get("namespace")
            
            # Assess affected services
            affected_services = self._identify_affected_services(k8s_state, service_name)
            
            # Check for data risk
            data_risk = self._assess_data_risk(k8s_state, detected_problems)
            
            # Calculate severity
            severity = self._calculate_severity(detected_problems, data_risk, affected_services)
            
            # Check incident status
            incident_status = self._check_incident_status(k8s_state, service_name)
            
            # SLO breach assessment
            slo_breach_risk = self._assess_slo_breach(detected_problems, severity)
            
            impact_assessment = {
                "severity": severity,
                "affected_services": affected_services,
                "slo_breach_risk": slo_breach_risk,
                "error_budget_remaining": "unknown",
                "data_risk": data_risk,
                "incident_status": incident_status,
                "blast_radius": len(affected_services)
            }
            
            state["impact_assessment"] = impact_assessment
            
            self._add_response(state, impact_assessment)
            
            if severity in ["SEV1", "SEV2"]:
                self._add_warning(state, f"{severity} incident detected - immediate action required")
            
        except Exception as e:
            self._add_error(state, f"Impact assessment failed: {str(e)}")
            state["impact_assessment"] = {
                "severity": "UNKNOWN",
                "affected_services": [],
                "slo_breach_risk": "unknown",
                "data_risk": False,
                "incident_status": "unknown"
            }
        
        return state
    
    def _identify_affected_services(self, k8s_state: Dict, primary_service: str) -> list:
        """Identify downstream affected services."""
        affected = [primary_service] if primary_service else []
        
        # In production: query service mesh or dependency graph
        # For now, check services in same namespace
        services = k8s_state.get("services", {}).get("items", [])
        for svc in services[:3]:  # Limit to avoid noise
            svc_name = svc.get("metadata", {}).get("name")
            if svc_name and svc_name != primary_service:
                affected.append(svc_name)
        
        return affected
    
    def _assess_data_risk(self, k8s_state: Dict, problems: list) -> bool:
        """Check if stateful components are involved."""
        # Check for PVC issues
        pvcs = k8s_state.get("persistentvolumeclaims", {}).get("items", [])
        if pvcs:
            for pvc in pvcs:
                status = pvc.get("status", {}).get("phase")
                if status != "Bound":
                    return True
        
        # Check problem descriptions for data-related keywords
        for problem in problems:
            desc = problem.get("description", "").lower()
            if any(keyword in desc for keyword in ["database", "storage", "pvc", "volume"]):
                return True
        
        return False
    
    def _calculate_severity(self, problems: list, data_risk: bool, affected_services: list) -> str:
        """Calculate incident severity."""
        if data_risk:
            return "SEV1"
        
        if len(affected_services) > 3:
            return "SEV1"
        
        critical_problems = [p for p in problems if p.get("severity") == "critical"]
        if critical_problems:
            return "SEV1"
        
        high_problems = [p for p in problems if p.get("severity") == "high"]
        if high_problems:
            return "SEV2"
        
        if len(affected_services) > 1:
            return "SEV3"
        
        return "SEV4"
    
    def _check_incident_status(self, k8s_state: Dict, service_name: str) -> str:
        """Check if incident is active or resolved."""
        pods = k8s_state.get("pods", {}).get("items", [])
        
        unhealthy_pods = 0
        for pod in pods:
            phase = pod.get("status", {}).get("phase")
            if phase not in ["Running", "Succeeded"]:
                unhealthy_pods += 1
        
        if unhealthy_pods > 0:
            return "active"
        else:
            return "resolved"
    
    def _assess_slo_breach(self, problems: list, severity: str) -> str:
        """Assess SLO breach risk."""
        if severity in ["SEV1", "SEV2"]:
            return "high"
        elif severity == "SEV3":
            return "medium"
        else:
            return "low"
