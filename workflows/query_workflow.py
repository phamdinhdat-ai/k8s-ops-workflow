"""QUERY mode workflow definition."""
from langgraph.graph import StateGraph, END
from typing import Dict, Any
from core.state import OperationState
from core.memory import MemoryStore
from agents import (
    ContextPreProcessorAgent,
    ResponseValidatorAgent,
    MemoryWriterAgent,
    ReportPlannerAgent,
    MetricsSummarizerAgent
)


def build_query_workflow(memory_store: MemoryStore):
    """Build the QUERY mode workflow graph."""
    
    # Initialize agents
    context_preprocessor = ContextPreProcessorAgent(memory_store)
    response_validator = ResponseValidatorAgent()
    memory_writer = MemoryWriterAgent(memory_store)
    report_planner = ReportPlannerAgent()
    metrics_summarizer = MetricsSummarizerAgent()
    
    # Define workflow
    workflow = StateGraph(OperationState)
    
    # Add nodes
    workflow.add_node("preprocess_context", context_preprocessor.execute)
    workflow.add_node("classify_intent", classify_intent_node)
    workflow.add_node("collect_k8s_state", collect_k8s_state_node)
    workflow.add_node("retrieve_knowledge", retrieve_knowledge_node)
    workflow.add_node("plan_report", report_planner.execute)
    workflow.add_node("summarize_metrics", metrics_summarizer.execute)
    workflow.add_node("validate_response", response_validator.execute)
    workflow.add_node("format_response", format_response_node)
    workflow.add_node("write_memory", memory_writer.execute)
    
    # Define edges
    workflow.set_entry_point("preprocess_context")
    workflow.add_edge("preprocess_context", "classify_intent")
    
    # Conditional routing from intent classifier
    workflow.add_conditional_edges(
        "classify_intent",
        route_by_intent,
        {
            "query_k8s": "collect_k8s_state",
            "query_knowledge": "retrieve_knowledge",
            "report": "plan_report",
            "end": END
        }
    )
    
    workflow.add_edge("collect_k8s_state", "validate_response")
    workflow.add_edge("retrieve_knowledge", "validate_response")
    workflow.add_edge("plan_report", "collect_k8s_state")
    workflow.add_edge("validate_response", "format_response")
    workflow.add_edge("format_response", "write_memory")
    workflow.add_edge("write_memory", END)
    
    return workflow.compile()


def classify_intent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Classify user intent."""
    query = state.get("user_query", "").lower()
    
    if "report" in query or "summary" in query:
        state["intent"] = "REPORT_REQUEST"
    elif "log" in query or "error" in query:
        state["intent"] = "QUERY_KNOWLEDGE"
    else:
        state["intent"] = "QUERY_K8S_STATE"
    
    state["intent_confidence"] = 0.8
    state["intent_reasoning"] = f"Classified as {state['intent']} based on keywords"
    
    return state


def route_by_intent(state: Dict[str, Any]) -> str:
    """Route based on classified intent."""
    intent = state.get("intent")
    
    if intent == "QUERY_K8S_STATE":
        return "query_k8s"
    elif intent == "QUERY_KNOWLEDGE":
        return "query_knowledge"
    elif intent == "REPORT_REQUEST":
        return "report"
    else:
        return "end"


def collect_k8s_state_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Collect K8s state (placeholder)."""
    namespace = state.get("user_context", {}).get("namespace", "default")
    
    state["k8s_state"] = {
        "namespace": namespace,
        "pods": {"items": []},
        "deployments": {"items": []},
        "services": {"items": []},
        "events": {"items": []}
    }
    
    return state


def retrieve_knowledge_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Retrieve knowledge (placeholder)."""
    state["knowledge_results"] = []
    return state


def format_response_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Format final response."""
    intent = state.get("intent")
    
    if intent == "QUERY_K8S_STATE":
        k8s_state = state.get("k8s_state", {})
        state["final_response"] = f"K8s state for namespace {k8s_state.get('namespace')}: {len(k8s_state.get('pods', {}).get('items', []))} pods found"
    elif intent == "QUERY_KNOWLEDGE":
        results = state.get("knowledge_results", [])
        state["final_response"] = f"Found {len(results)} knowledge base results"
    elif intent == "REPORT_REQUEST":
        report_plan = state.get("report_plan", {})
        state["final_response"] = f"Report generated using {report_plan.get('template')} template"
    else:
        state["final_response"] = "Query processed"
    
    return state
