"""State definition for the workflow."""
from typing import TypedDict, Optional, Dict, Any, List


class OperationState(TypedDict):
    """Complete state shape for K8s operations workflow."""
    
    # Identity
    session_id: str
    workflow_id: str
    created_at: str

    # Input
    user_query: str
    user_context: Dict[str, Any]
    rca_mode: bool
    rca_trigger: Optional[str]

    # Classification
    intent: Optional[str]
    intent_confidence: float
    intent_entities: Dict[str, Any]
    intent_reasoning: str

    # HITL
    hitl_pending: bool
    hitl_question: Optional[str]
    hitl_response: Optional[str]
    hitl_gate: Optional[str]
    context_enriched: bool

    # Data collected
    k8s_state: Optional[Dict[str, Any]]
    knowledge_results: List[Dict[str, Any]]
    log_trace_evidence: Optional[Dict[str, Any]]
    change_events: List[Dict[str, Any]]
    metrics_summary: Optional[Dict[str, Any]]
    evidence: Optional[Dict[str, Any]]

    # RCA Analysis
    timeline: Optional[Dict[str, Any]]
    detected_problems: List[Dict[str, Any]]
    root_cause: Optional[Dict[str, Any]]
    impact_assessment: Optional[Dict[str, Any]]
    remediation_suggestions: List[Dict[str, Any]]

    # Validation
    validation_result: Optional[Dict[str, Any]]

    # Report
    report_plan: Optional[Dict[str, Any]]
    report: Optional[Dict[str, Any]]

    # Output
    final_response: Optional[str]

    # Memory
    conversation_history: List[Dict[str, str]]
    memory_context: Optional[Dict[str, Any]]

    # Meta
    current_phase: str
    workflow_mode: str
    errors: List[str]
    warnings: List[str]
    agent_responses: List[Dict[str, Any]]
