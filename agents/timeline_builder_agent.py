"""Timeline builder agent - merges evidence into chronological timeline."""
from typing import Dict, Any, List
from datetime import datetime
from core.base_agent import BaseAgent


class TimelineBuilderAgent(BaseAgent):
    """Builds chronological timeline from all evidence sources."""
    
    def __init__(self):
        super().__init__("TimelineBuilder")
    
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Merge and sort all evidence into timeline."""
        try:
            all_events = []
            
            # Collect change events
            change_events = state.get("change_events", [])
            for event in change_events:
                all_events.append({
                    "timestamp": event["timestamp"],
                    "source": "k8s_change",
                    "type": event["type"],
                    "description": event["description"],
                    "resource": event.get("resource"),
                    "severity": self._classify_severity(event)
                })
            
            # Collect log/trace evidence
            log_evidence = state.get("log_trace_evidence", {})
            if log_evidence:
                for error_log in log_evidence.get("error_logs", []):
                    all_events.append({
                        "timestamp": error_log.get("timestamp"),
                        "source": "error_log",
                        "type": "Error",
                        "description": error_log.get("message"),
                        "severity": "high"
                    })
            
            # Sort by timestamp
            all_events.sort(key=lambda x: x["timestamp"] if x["timestamp"] else "")
            
            # Identify key timestamps
            t0 = self._identify_t0(all_events)
            t_impact = self._identify_t_impact(all_events)
            t_change = self._identify_t_change(all_events, t0)
            
            # Build narrative
            narrative = self._build_narrative(all_events, t0, t_impact, t_change)
            
            # Identify likely trigger
            likely_trigger = self._identify_trigger(all_events, t0)
            
            timeline = {
                "t0": t0,
                "t_impact": t_impact,
                "t_change": t_change,
                "events": all_events,
                "likely_trigger": likely_trigger,
                "narrative": narrative
            }
            
            state["timeline"] = timeline
            
            self._add_response(state, {
                "total_events": len(all_events),
                "t0": t0,
                "likely_trigger": likely_trigger.get("description") if likely_trigger else None
            })
            
        except Exception as e:
            self._add_error(state, f"Timeline building failed: {str(e)}")
            state["timeline"] = None
        
        return state
    
    def _identify_t0(self, events: List[Dict]) -> str:
        """Identify first anomaly timestamp."""
        for event in events:
            if event["severity"] in ["high", "critical"]:
                return event["timestamp"]
        return events[0]["timestamp"] if events else None
    
    def _identify_t_impact(self, events: List[Dict]) -> str:
        """Identify when user-facing impact started."""
        for event in events:
            if "5xx" in event["description"] or "timeout" in event["description"].lower():
                return event["timestamp"]
        return None
    
    def _identify_t_change(self, events: List[Dict], t0: str) -> str:
        """Identify most recent change before T0."""
        if not t0:
            return None
        
        for event in reversed(events):
            if event["timestamp"] < t0 and event["source"] == "k8s_change":
                return event["timestamp"]
        return None
    
    def _identify_trigger(self, events: List[Dict], t0: str) -> Dict:
        """Identify most likely trigger event."""
        if not t0 or not events:
            return None
        
        # Find event closest to T0 with high correlation
        candidates = [e for e in events if e["timestamp"] <= t0]
        if candidates:
            return candidates[-1]
        return None
    
    def _classify_severity(self, event: Dict) -> str:
        """Classify event severity."""
        event_type = event.get("type", "").lower()
        description = event.get("description", "").lower()
        
        if "error" in event_type or "failed" in description:
            return "high"
        elif "warning" in event_type:
            return "medium"
        else:
            return "low"
    
    def _build_narrative(self, events: List[Dict], t0: str, t_impact: str, t_change: str) -> str:
        """Build human-readable narrative."""
        narrative_parts = []
        
        if t_change:
            narrative_parts.append(f"[T-change] Recent change detected at {t_change}")
        
        if t0:
            narrative_parts.append(f"[T0] First anomaly at {t0}")
        
        if t_impact:
            narrative_parts.append(f"[T-impact] User-facing impact at {t_impact}")
        
        return " → ".join(narrative_parts)
