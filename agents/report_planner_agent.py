"""Report planner agent - structures report scope and template."""
from typing import Dict, Any
from core.base_agent import BaseAgent


class ReportPlannerAgent(BaseAgent):
    """Plans report structure, template, and complexity."""
    
    TEMPLATES = {
        "health_summary": ["overview", "pod_status", "resource_usage", "recent_events"],
        "incident_summary": ["timeline", "impact", "root_cause", "remediation"],
        "capacity_overview": ["resource_usage", "hpa_status", "node_capacity", "recommendations"],
        "deployment_status": ["deployments", "rollout_history", "replica_status", "health_checks"],
        "full_audit": ["all_resources", "security", "compliance", "recommendations"]
    }
    
    def __init__(self):
        super().__init__("ReportPlanner")
    
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Plan report structure and determine complexity."""
        try:
            user_query = state.get("user_query", "")
            user_context = state.get("user_context", {})
            intent_entities = state.get("intent_entities", {})
            
            # Determine template
            template = self._select_template(user_query, intent_entities)
            
            # Determine scope
            namespaces = []
            if user_context.get("namespace"):
                namespaces = [user_context["namespace"]]
            elif "all" in user_query.lower() or "cluster" in user_query.lower():
                namespaces = ["all"]
            
            # Resources to query
            resources_to_query = self._determine_resources(template, intent_entities)
            
            # Complexity assessment
            resource_count = len(resources_to_query)
            is_multi_namespace = len(namespaces) > 1 or "all" in namespaces
            needs_hitl = is_multi_namespace or resource_count > 10
            
            report_plan = {
                "template": template,
                "sections": self.TEMPLATES.get(template, ["overview"]),
                "resources_to_query": resources_to_query,
                "namespaces": namespaces,
                "needs_scope_confirmation": needs_hitl,
                "complexity": "complex" if needs_hitl else "simple"
            }
            
            state["report_plan"] = report_plan
            self._add_response(state, report_plan)
            
        except Exception as e:
            self._add_error(state, f"Report planning failed: {str(e)}")
            state["report_plan"] = {
                "template": "health_summary",
                "sections": ["overview"],
                "resources_to_query": ["pods", "deployments"],
                "namespaces": [user_context.get("namespace", "default")],
                "needs_scope_confirmation": False,
                "complexity": "simple"
            }
        
        return state
    
    def _select_template(self, query: str, entities: Dict[str, Any]) -> str:
        """Select appropriate report template."""
        query_lower = query.lower()
        
        if "incident" in query_lower or "rca" in query_lower:
            return "incident_summary"
        elif "capacity" in query_lower or "resource" in query_lower:
            return "capacity_overview"
        elif "deployment" in query_lower or "rollout" in query_lower:
            return "deployment_status"
        elif "audit" in query_lower or "full" in query_lower:
            return "full_audit"
        else:
            return "health_summary"
    
    def _determine_resources(self, template: str, entities: Dict[str, Any]) -> list:
        """Determine which K8s resources to query."""
        base_resources = ["pods", "deployments", "services"]
        
        if template == "capacity_overview":
            return base_resources + ["hpa", "nodes", "pvc"]
        elif template == "deployment_status":
            return ["deployments", "replicasets", "pods"]
        elif template == "full_audit":
            return base_resources + ["configmaps", "secrets", "ingress", "networkpolicies"]
        else:
            return base_resources + ["events"]
