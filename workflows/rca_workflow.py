"""RCA mode workflow definition."""
from langgraph.graph import StateGraph, END
from typing import Dict, Any
from core.state import OperationState
from core.memory import MemoryStore
from agents import (
    ContextPreProcessorAgent,
    MemoryWriterAgent,
    LogTraceRetrieverAgent,
    ChangeEventDetectorAgent,
    TimelineBuilderAgent,
    ImpactAssessorAgent
)


def build_rca_workflow(memory_store: MemoryStore):
    """Build the RCA mode workflow graph."""
    
    # Initialize agents
    context_preprocessor = ContextPreProcessorAgent(memory_store)
    memory_writer = MemoryWriterAgent(memory_store)
    log_trace_retriever = LogTraceRetrieverAgent()
    change_detector = ChangeEventDetectorAgent()
    timeline_builder = TimelineBuilderAgent()
    impact_assessor = ImpactAssessorAgent()
    
    # Define workflow
    workflow = StateGraph(OperationState)
    
    # Add nodes
    workflow.add_node("preprocess_context", context_preprocessor.execute)
    workflow.add_node("rca_intake", rca_intake_node)
    workflow.add_node("collect_k8s_state", collect_k8s_state_node)
    workflow.add_node("collect_logs", log_trace_retriever.execute)
    workflow.add_node("detect_changes", change_detector.execute)
    workflow.add_node("build_timeline", timeline_builder.execute)
    workflow.add_node("detect_problems", detect_problems_node)
    workflow.add_node("analyze_root_cause", analyze_root_cause_node)
    workflow.add_node("assess_impact", impact_assessor.execute)
    workflow.add_node("plan_remediation", plan_remediation_node)
    workflow.add_node("generate_rca_report", generate_rca_report_node)
    workflow.add_node("write_memory", memory_writer.execute)
    
    # Define edges
    workflow.set_entry_point("preprocess_context")
    workflow.add_edge("preprocess_context", "rca_intake")
    workflow.add_edge("rca_intake", "collect_k8s_state")
    workflow.add_edge("collect_k8s_state", "collect_logs")
    workflow.add_edge("collect_logs", "detect_changes")
    workflow.add_edge("detect_changes", "build_timeline")
    workflow.add_edge("build_timeline", "detect_problems")
    workflow.add_edge("detect_problems", "analyze_root_cause")
    workflow.add_edge("analyze_root_cause", "assess_impact")
    workflow.add_edge("assess_impact", "plan_remediation")
    workflow.add_edge("plan_remediation", "generate_rca_report")
    workflow.add_edge("generate_rca_report", "write_memory")
    workflow.add_edge("write_memory", END)
    
    return workflow.compile()


def rca_intake_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Structure RCA investigation scope."""
    user_context = state.get("user_context", {})
    
    state["current_phase"] = "rca_intake"
    state["workflow_mode"] = "RCA"
    
    # Ensure required context
    if not user_context.get("service_name"):
        state["hitl_pending"] = True
        state["hitl_question"] = "Please provide the service name for investigation"
        state["hitl_gate"] = "context_gate"
    
    return state


def collect_k8s_state_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Collect K8s state for RCA."""
    namespace = state.get("user_context", {}).get("namespace", "default")
    service_name = state.get("user_context", {}).get("service_name")
    
    state["k8s_state"] = {
        "namespace": namespace,
        "service": service_name,
        "pods": {"items": []},
        "deployments": {"items": []},
        "services": {"items": []},
        "events": {"items": []}
    }
    
    return state


def detect_problems_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Detect problems from timeline and evidence."""
    timeline = state.get("timeline", {})
    
    problems = []
    
    # Analyze timeline events
    events = timeline.get("events", [])
    for event in events:
        if event.get("severity") in ["high", "critical"]:
            problems.append({
                "type": event.get("type"),
                "description": event.get("description"),
                "severity": event.get("severity"),
                "timestamp": event.get("timestamp")
            })
    
    state["detected_problems"] = problems
    return state


def analyze_root_cause_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze root cause from problems and timeline."""
    timeline = state.get("timeline", {})
    problems = state.get("detected_problems", [])
    
    likely_trigger = timeline.get("likely_trigger")
    
    root_cause = {
        "primary_hypothesis": {
            "description": likely_trigger.get("description") if likely_trigger else "Unknown",
            "confidence": 0.7,
            "evidence": [p.get("description") for p in problems[:3]]
        },
        "alternative_hypotheses": []
    }
    
    state["root_cause"] = root_cause
    return state


def plan_remediation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Plan remediation steps."""
    root_cause = state.get("root_cause", {})
    
    remediation_suggestions = [
        {
            "step": "Rollback deployment",
            "risk": "low",
            "priority": 1,
            "command": "kubectl rollout undo deployment/<name>"
        },
        {
            "step": "Scale up replicas",
            "risk": "low",
            "priority": 2,
            "command": "kubectl scale deployment/<name> --replicas=3"
        }
    ]
    
    state["remediation_suggestions"] = remediation_suggestions
    return state


def generate_rca_report_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Generate RCA report."""
    timeline = state.get("timeline", {})
    root_cause = state.get("root_cause", {})
    impact = state.get("impact_assessment", {})
    remediation = state.get("remediation_suggestions", [])
    
    report = f"""
# Root Cause Analysis Report

## Incident Summary
- Service: {state.get('user_context', {}).get('service_name')}
- Namespace: {state.get('user_context', {}).get('namespace')}
- Severity: {impact.get('severity', 'UNKNOWN')}
- Status: {impact.get('incident_status', 'unknown')}

## Timeline
{timeline.get('narrative', 'No timeline available')}

## Root Cause
{root_cause.get('primary_hypothesis', {}).get('description', 'Unknown')}

Confidence: {root_cause.get('primary_hypothesis', {}).get('confidence', 0) * 100}%

## Impact Assessment
- Affected Services: {len(impact.get('affected_services', []))}
- SLO Breach Risk: {impact.get('slo_breach_risk', 'unknown')}
- Data Risk: {impact.get('data_risk', False)}

## Remediation Steps
"""
    
    for i, step in enumerate(remediation, 1):
        report += f"\n{i}. {step.get('step')} (Risk: {step.get('risk')})\n   `{step.get('command')}`"
    
    state["final_response"] = report
    return state
