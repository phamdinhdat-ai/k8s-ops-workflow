"""Main entry point for K8s Operations Workflow."""
import os
import uuid
from datetime import datetime
from dotenv import load_dotenv
from core.memory import MemoryStore
from core.state import OperationState
from workflows.query_workflow import build_query_workflow
from workflows.rca_workflow import build_rca_workflow


def create_initial_state(user_query: str, rca_mode: bool = False) -> OperationState:
    """Create initial workflow state."""
    return {
        "session_id": str(uuid.uuid4()),
        "workflow_id": str(uuid.uuid4()),
        "created_at": datetime.utcnow().isoformat(),
        "user_query": user_query,
        "user_context": {},
        "rca_mode": rca_mode,
        "rca_trigger": None,
        "intent": None,
        "intent_confidence": 0.0,
        "intent_entities": {},
        "intent_reasoning": "",
        "hitl_pending": False,
        "hitl_question": None,
        "hitl_response": None,
        "hitl_gate": None,
        "context_enriched": False,
        "k8s_state": None,
        "knowledge_results": [],
        "log_trace_evidence": None,
        "change_events": [],
        "metrics_summary": None,
        "evidence": None,
        "timeline": None,
        "detected_problems": [],
        "root_cause": None,
        "impact_assessment": None,
        "remediation_suggestions": [],
        "validation_result": None,
        "report_plan": None,
        "report": None,
        "final_response": None,
        "conversation_history": [],
        "memory_context": None,
        "current_phase": "init",
        "workflow_mode": "RCA" if rca_mode else "QUERY",
        "errors": [],
        "warnings": [],
        "agent_responses": []
    }


async def run_workflow(user_query: str, rca_mode: bool = False, user_context: dict = None):
    """Run the appropriate workflow based on mode."""
    load_dotenv()
    
    # Initialize memory store
    memory_store = MemoryStore()
    
    # Create initial state
    state = create_initial_state(user_query, rca_mode)
    if user_context:
        state["user_context"] = user_context
    
    # Build and run workflow
    if rca_mode:
        workflow = build_rca_workflow(memory_store)
    else:
        workflow = build_query_workflow(memory_store)
    
    # Execute workflow
    result = await workflow.ainvoke(state)
    
    return result


def main():
    """CLI entry point."""
    import asyncio
    
    print("K8s Operations Workflow")
    print("=" * 50)
    
    # Example QUERY mode
    print("\n[QUERY Mode Example]")
    query_result = asyncio.run(run_workflow(
        user_query="Show me pods in production namespace",
        rca_mode=False,
        user_context={"namespace": "production"}
    ))
    print(f"Response: {query_result.get('final_response')}")
    
    # Example RCA mode
    print("\n[RCA Mode Example]")
    rca_result = asyncio.run(run_workflow(
        user_query="Investigate payment-service outage",
        rca_mode=True,
        user_context={
            "namespace": "production",
            "service_name": "payment-service",
            "time_range": "1h"
        }
    ))
    print(f"Response: {rca_result.get('final_response')}")


if __name__ == "__main__":
    main()
