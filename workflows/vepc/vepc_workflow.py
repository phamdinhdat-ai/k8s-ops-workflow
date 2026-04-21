"""vEPC workflow definition."""
from langgraph.graph import StateGraph, END
from typing import Dict, Any
from core.vepc_state import VEPCState
from agents.vepc import (
    QueryRewriterAgent,
    IntentClassifierAgent,
    KnowledgeRetrieverAgent,
    CLIGeneratorAgent,
    CLIValidatorAgent,
    RiskAssessorAgent,
    ResponseSynthesizerAgent,
)
from config.vepc_settings import VEPC_MAX_VALIDATION_RETRIES
import uuid
from datetime import datetime


def build_vepc_workflow():
    """Build the vEPC workflow graph."""

    # Initialize agents
    query_rewriter = QueryRewriterAgent()
    intent_classifier = IntentClassifierAgent()
    knowledge_retriever = KnowledgeRetrieverAgent()
    cli_generator = CLIGeneratorAgent()
    cli_validator = CLIValidatorAgent()
    risk_assessor = RiskAssessorAgent()
    response_synthesizer = ResponseSynthesizerAgent()

    # Define workflow
    workflow = StateGraph(VEPCState)

    # Add nodes
    workflow.add_node("rewrite_query", query_rewriter.execute)
    workflow.add_node("classify_intent", intent_classifier.execute)
    workflow.add_node("retrieve_knowledge", knowledge_retriever.execute)
    workflow.add_node("generate_cli", cli_generator.execute)
    workflow.add_node("validate_cli", cli_validator.execute)
    workflow.add_node("assess_risk", risk_assessor.execute)
    workflow.add_node("synthesize_response", response_synthesizer.execute)

    # Define edges
    workflow.set_entry_point("rewrite_query")
    workflow.add_edge("rewrite_query", "classify_intent")
    workflow.add_edge("classify_intent", "retrieve_knowledge")

    # Conditional routing after knowledge retrieval
    workflow.add_conditional_edges(
        "retrieve_knowledge",
        route_by_intent,
        {
            "generate_cli": "generate_cli",
            "synthesize": "synthesize_response",
        },
    )

    # CLI path: generate -> validate -> check validation
    workflow.add_edge("generate_cli", "validate_cli")
    workflow.add_conditional_edges(
        "validate_cli",
        check_validation,
        {
            "retry": "generate_cli",
            "assess_risk": "assess_risk",
            "synthesize": "synthesize_response",
        },
    )

    # Risk assessment -> synthesize
    workflow.add_edge("assess_risk", "synthesize_response")

    # End
    workflow.add_edge("synthesize_response", END)

    return workflow.compile()


def route_by_intent(state: VEPCState) -> str:
    """Route based on intent classification."""
    intent = state.get("intent", "general")

    # CLI generation needed for show/update intents
    if intent in ["show", "update"]:
        return "generate_cli"

    # Direct to synthesis for explain/troubleshoot/general
    return "synthesize"


def check_validation(state: VEPCState) -> str:
    """Check CLI validation result and decide next step."""
    validation_passed = state.get("validation_passed", False)
    validation_attempts = state.get("validation_attempts", 0)
    intent = state.get("intent", "show")

    # If validation passed
    if validation_passed:
        # Assess risk for update operations
        if intent == "update":
            return "assess_risk"
        # Skip risk assessment for show operations
        return "synthesize"

    # If validation failed, check retry limit
    if validation_attempts < VEPC_MAX_VALIDATION_RETRIES:
        return "retry"

    # Max retries reached, proceed to synthesis with errors
    return "synthesize"


async def run_vepc_workflow(
    user_query: str,
    language: str = "en",
    conversation_history: list = None,
) -> Dict[str, Any]:
    """
    Run the vEPC workflow.

    Args:
        user_query: User's natural language query
        language: Language code ("en" or "vi")
        conversation_history: Previous conversation turns

    Returns:
        Dictionary containing final response and metadata
    """
    # Build workflow
    workflow = build_vepc_workflow()

    # Initialize state
    initial_state: VEPCState = {
        "session_id": str(uuid.uuid4()),
        "workflow_id": str(uuid.uuid4()),
        "created_at": datetime.utcnow().isoformat(),
        "user_query": user_query,
        "language": language,
        "conversation_history": conversation_history or [],
        "rewritten_query": None,
        "rewrite_reasoning": None,
        "intent": None,
        "intent_confidence": 0.0,
        "intent_entities": {},
        "intent_reasoning": "",
        "knowledge_results": [],
        "knowledge_context": None,
        "cli_commands": [],
        "cli_explanation": None,
        "cli_generation_reasoning": None,
        "validation_attempts": 0,
        "validation_passed": False,
        "validation_errors": [],
        "validation_warnings": [],
        "risk_level": None,
        "risk_warnings": [],
        "impact_description": None,
        "affected_components": [],
        "final_response": "",
        "response_metadata": {},
        "errors": [],
        "warnings": [],
        "retry_count": 0,
    }

    # Execute workflow
    result = await workflow.ainvoke(initial_state)

    return {
        "final_response": result["final_response"],
        "intent": result.get("intent"),
        "cli_commands": result.get("cli_commands", []),
        "risk_level": result.get("risk_level"),
        "validation_passed": result.get("validation_passed"),
        "metadata": result.get("response_metadata", {}),
    }
