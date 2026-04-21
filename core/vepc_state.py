"""State definition for vEPC workflow."""
from typing import TypedDict, Optional, Dict, Any, List


class VEPCState(TypedDict):
    """Complete state shape for vEPC workflow."""

    # Identity
    session_id: str
    workflow_id: str
    created_at: str

    # Input
    user_query: str
    language: str  # "en" or "vi"
    conversation_history: List[Dict[str, str]]

    # Query processing
    rewritten_query: Optional[str]
    rewrite_reasoning: Optional[str]

    # Intent classification
    intent: Optional[str]  # show/update/explain/troubleshoot/general
    intent_confidence: float
    intent_entities: Dict[str, Any]
    intent_reasoning: str

    # Knowledge retrieval
    knowledge_results: List[Dict[str, Any]]
    knowledge_context: Optional[str]

    # CLI generation (for show/update intents)
    cli_commands: List[str]
    cli_explanation: Optional[str]
    cli_generation_reasoning: Optional[str]

    # CLI validation
    validation_attempts: int
    validation_passed: bool
    validation_errors: List[str]
    validation_warnings: List[str]

    # Risk assessment (for update intent)
    risk_level: Optional[str]  # low/medium/high/critical
    risk_warnings: List[str]
    impact_description: Optional[str]
    affected_components: List[str]

    # Response synthesis
    final_response: str
    response_metadata: Dict[str, Any]

    # Error handling
    errors: List[str]
    warnings: List[str]
    retry_count: int
