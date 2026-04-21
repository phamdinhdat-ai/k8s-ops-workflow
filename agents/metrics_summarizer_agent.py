"""Metrics summarizer agent - collects CPU/memory/restart metrics."""
from typing import Dict, Any
from core.base_agent import BaseAgent


class MetricsSummarizerAgent(BaseAgent):
    """Summarizes resource metrics for reports."""
    
    def __init__(self):
        super().__init__("MetricsSummarizer")
    
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Collect and summarize resource metrics."""
        try:
            namespace = state.get("user_context", {}).get("namespace", "default")
            k8s_state = state.get("k8s_state", {})
            
            metrics_summary = {
                "namespace": namespace,
                "pod_metrics": [],
                "namespace_totals": {
                    "total_pods": 0,
                    "total_restarts": 0,
                    "pods_near_limit": []
                },
                "warnings": []
            }
            
            # Extract pod metrics from k8s_state
            pods = k8s_state.get("pods", {}).get("items", [])
            
            for pod in pods:
                pod_name = pod.get("metadata", {}).get("name", "unknown")
                
                # Extract restart counts
                restart_count = 0
                containers = pod.get("status", {}).get("containerStatuses", [])
                for container in containers:
                    restart_count += container.get("restartCount", 0)
                
                # Extract resource usage (if available from kubectl top)
                cpu_usage = "N/A"
                memory_usage = "N/A"
                
                pod_metric = {
                    "name": pod_name,
                    "restarts": restart_count,
                    "cpu_usage": cpu_usage,
                    "memory_usage": memory_usage,
                    "status": pod.get("status", {}).get("phase", "Unknown")
                }
                
                metrics_summary["pod_metrics"].append(pod_metric)
                metrics_summary["namespace_totals"]["total_restarts"] += restart_count
                
                # Flag high restart counts
                if restart_count > 5:
                    metrics_summary["warnings"].append(
                        f"Pod {pod_name} has {restart_count} restarts"
                    )
                    metrics_summary["namespace_totals"]["pods_near_limit"].append(pod_name)
            
            metrics_summary["namespace_totals"]["total_pods"] = len(pods)
            
            state["metrics_summary"] = metrics_summary
            
            for warning in metrics_summary["warnings"]:
                self._add_warning(state, warning)
            
            self._add_response(state, {
                "total_pods": metrics_summary["namespace_totals"]["total_pods"],
                "total_restarts": metrics_summary["namespace_totals"]["total_restarts"],
                "warnings_count": len(metrics_summary["warnings"])
            })
            
        except Exception as e:
            self._add_error(state, f"Metrics summarization failed: {str(e)}")
            state["metrics_summary"] = None
        
        return state
