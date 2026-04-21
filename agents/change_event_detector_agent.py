"""Change event detector agent - detects recent K8s changes."""
from typing import Dict, Any
from datetime import datetime, timedelta
from core.base_agent import BaseAgent


class ChangeEventDetectorAgent(BaseAgent):
    """Detects recent changes that may correlate with incidents."""
    
    def __init__(self):
        super().__init__("ChangeEventDetector")
    
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Detect changes near incident time."""
        try:
            user_context = state.get("user_context", {})
            namespace = user_context.get("namespace")
            k8s_state = state.get("k8s_state", {})
            
            # Parse incident time
            time_range = user_context.get("time_range", "1h")
            incident_time = datetime.utcnow()
            lookback_window = self._parse_lookback(time_range)
            
            change_events = []
            
            # Check K8s events
            events = k8s_state.get("events", {}).get("items", [])
            for event in events:
                event_time = self._parse_k8s_time(event.get("lastTimestamp"))
                if event_time and (incident_time - event_time) < lookback_window:
                    correlation_score = self._calculate_correlation(event_time, incident_time)
                    
                    change_events.append({
                        "timestamp": event_time.isoformat(),
                        "type": event.get("type", "Normal"),
                        "reason": event.get("reason", "Unknown"),
                        "resource": f"{event.get('involvedObject', {}).get('kind')}/{event.get('involvedObject', {}).get('name')}",
                        "description": event.get("message", ""),
                        "correlation_score": correlation_score
                    })
            
            # Check deployment changes
            deployments = k8s_state.get("deployments", {}).get("items", [])
            for deployment in deployments:
                # Check for recent rollouts
                conditions = deployment.get("status", {}).get("conditions", [])
                for condition in conditions:
                    if condition.get("type") == "Progressing":
                        last_update = self._parse_k8s_time(condition.get("lastUpdateTime"))
                        if last_update and (incident_time - last_update) < lookback_window:
                            correlation_score = self._calculate_correlation(last_update, incident_time)
                            
                            change_events.append({
                                "timestamp": last_update.isoformat(),
                                "type": "Deployment",
                                "reason": "Rollout",
                                "resource": f"Deployment/{deployment.get('metadata', {}).get('name')}",
                                "description": f"Deployment rollout: {condition.get('message', '')}",
                                "correlation_score": correlation_score
                            })
            
            # Sort by correlation score
            change_events.sort(key=lambda x: x["correlation_score"], reverse=True)
            
            state["change_events"] = change_events
            
            self._add_response(state, {
                "total_changes": len(change_events),
                "high_correlation_changes": len([e for e in change_events if e["correlation_score"] > 0.7])
            })
            
            if change_events and change_events[0]["correlation_score"] > 0.8:
                self._add_warning(state, f"High correlation change detected: {change_events[0]['description']}")
            
        except Exception as e:
            self._add_error(state, f"Change detection failed: {str(e)}")
            state["change_events"] = []
        
        return state
    
    def _parse_lookback(self, time_range: str) -> timedelta:
        """Parse time range to timedelta."""
        if time_range.endswith("h"):
            return timedelta(hours=int(time_range[:-1]) + 1)
        elif time_range.endswith("m"):
            return timedelta(minutes=int(time_range[:-1]) + 30)
        return timedelta(hours=2)
    
    def _parse_k8s_time(self, time_str: str) -> datetime:
        """Parse Kubernetes timestamp."""
        if not time_str:
            return None
        try:
            return datetime.fromisoformat(time_str.replace("Z", "+00:00"))
        except:
            return None
    
    def _calculate_correlation(self, change_time: datetime, incident_time: datetime) -> float:
        """Calculate correlation score based on time proximity."""
        time_diff = abs((incident_time - change_time).total_seconds())
        
        # Within 30 minutes: high correlation
        if time_diff < 1800:
            return 0.9
        # Within 1 hour: medium correlation
        elif time_diff < 3600:
            return 0.7
        # Within 2 hours: low correlation
        elif time_diff < 7200:
            return 0.5
        else:
            return 0.3
