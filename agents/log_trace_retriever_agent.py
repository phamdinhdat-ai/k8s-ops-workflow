"""Log trace retriever agent - time-bounded log/trace queries."""
from typing import Dict, Any
from datetime import datetime, timedelta
from core.base_agent import BaseAgent


class LogTraceRetrieverAgent(BaseAgent):
    """Retrieves time-bounded logs and traces for RCA."""
    
    def __init__(self):
        super().__init__("LogTraceRetriever")
    
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve logs and traces for incident window."""
        try:
            user_context = state.get("user_context", {})
            service_name = user_context.get("service_name")
            namespace = user_context.get("namespace")
            
            # Parse time range
            time_range = user_context.get("time_range", "1h")
            start_time, end_time = self._parse_time_range(time_range)
            
            # Extract error keywords from query
            error_keywords = self._extract_error_keywords(state.get("user_query", ""))
            
            # Simulate log retrieval (in production, query VectorDB)
            log_trace_evidence = {
                "service": service_name,
                "namespace": namespace,
                "time_window": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat()
                },
                "error_logs": [],
                "stack_traces": [],
                "slow_spans": [],
                "error_rate_timeline": [],
                "error_signatures": []
            }
            
            # In production: query VectorDB with filters
            # For now, return structured placeholder
            log_trace_evidence["error_signatures"] = error_keywords
            
            state["log_trace_evidence"] = log_trace_evidence
            
            self._add_response(state, {
                "service": service_name,
                "time_window": f"{start_time} to {end_time}",
                "error_logs_count": len(log_trace_evidence["error_logs"]),
                "stack_traces_count": len(log_trace_evidence["stack_traces"])
            })
            
        except Exception as e:
            self._add_error(state, f"Log/trace retrieval failed: {str(e)}")
            state["log_trace_evidence"] = None
        
        return state
    
    def _parse_time_range(self, time_range: str) -> tuple:
        """Parse time range string to datetime objects."""
        end_time = datetime.utcnow()
        
        if time_range.endswith("h"):
            hours = int(time_range[:-1])
            start_time = end_time - timedelta(hours=hours)
        elif time_range.endswith("m"):
            minutes = int(time_range[:-1])
            start_time = end_time - timedelta(minutes=minutes)
        else:
            start_time = end_time - timedelta(hours=1)
        
        return start_time, end_time
    
    def _extract_error_keywords(self, query: str) -> list:
        """Extract error-related keywords from query."""
        keywords = []
        error_terms = ["error", "exception", "timeout", "crash", "fail", "oom"]
        
        for term in error_terms:
            if term in query.lower():
                keywords.append(term)
        
        return keywords
