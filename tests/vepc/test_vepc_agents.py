"""Tests for vEPC agents."""
import pytest
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
import uuid
from datetime import datetime


@pytest.fixture
def base_state():
    """Create a base state for testing."""
    return {
        "session_id": str(uuid.uuid4()),
        "workflow_id": str(uuid.uuid4()),
        "created_at": datetime.utcnow().isoformat(),
        "user_query": "Show me the current MCC and MNC",
        "language": "en",
        "conversation_history": [],
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


@pytest.mark.asyncio
async def test_query_rewriter_standalone(base_state):
    """Test query rewriter with standalone query."""
    agent = QueryRewriterAgent()
    result = await agent.execute(base_state)

    assert result["rewritten_query"] is not None
    assert result["rewrite_reasoning"] is not None


@pytest.mark.asyncio
async def test_query_rewriter_with_context(base_state):
    """Test query rewriter with conversation context."""
    base_state["user_query"] = "change it to 90"
    base_state["conversation_history"] = [
        {
            "user": "Set timer T3412 to 60 minutes",
            "assistant": "Here is the command: set timer t3412 60",
        }
    ]

    agent = QueryRewriterAgent()
    result = await agent.execute(base_state)

    assert result["rewritten_query"] is not None
    assert "t3412" in result["rewritten_query"].lower() or "timer" in result["rewritten_query"].lower()


@pytest.mark.asyncio
async def test_intent_classifier_show(base_state):
    """Test intent classifier for show intent."""
    base_state["user_query"] = "Show me the current MCC and MNC"
    base_state["rewritten_query"] = "Show me the current MCC and MNC"

    agent = IntentClassifierAgent()
    result = await agent.execute(base_state)

    assert result["intent"] == "show"
    assert result["intent_confidence"] > 0.5


@pytest.mark.asyncio
async def test_intent_classifier_update(base_state):
    """Test intent classifier for update intent."""
    base_state["user_query"] = "Set timer T3412 to 60 minutes"
    base_state["rewritten_query"] = "Set timer T3412 to 60 minutes"

    agent = IntentClassifierAgent()
    result = await agent.execute(base_state)

    assert result["intent"] == "update"
    assert result["intent_confidence"] > 0.5


@pytest.mark.asyncio
async def test_intent_classifier_explain(base_state):
    """Test intent classifier for explain intent."""
    base_state["user_query"] = "What does the T3412 timer do?"
    base_state["rewritten_query"] = "What does the T3412 timer do?"

    agent = IntentClassifierAgent()
    result = await agent.execute(base_state)

    assert result["intent"] == "explain"


@pytest.mark.asyncio
async def test_knowledge_retriever_skip_general(base_state):
    """Test knowledge retriever skips general intent."""
    base_state["intent"] = "general"

    agent = KnowledgeRetrieverAgent()
    result = await agent.execute(base_state)

    assert result["knowledge_results"] == []
    assert result["knowledge_context"] == ""


@pytest.mark.asyncio
async def test_cli_generator(base_state):
    """Test CLI generator."""
    base_state["intent"] = "show"
    base_state["rewritten_query"] = "Show me the current MCC and MNC"
    base_state["intent_entities"] = {"parameter": "mcc, mnc"}

    agent = CLIGeneratorAgent()
    result = await agent.execute(base_state)

    assert len(result["cli_commands"]) > 0
    assert result["cli_explanation"] is not None


@pytest.mark.asyncio
async def test_cli_validator_empty_commands(base_state):
    """Test CLI validator with no commands."""
    agent = CLIValidatorAgent()
    result = await agent.execute(base_state)

    assert result["validation_passed"] is True
    assert result["validation_errors"] == []


@pytest.mark.asyncio
async def test_risk_assessor_show_intent(base_state):
    """Test risk assessor for show intent (should be low risk)."""
    base_state["intent"] = "show"
    base_state["cli_commands"] = ["show mcc"]

    agent = RiskAssessorAgent()
    result = await agent.execute(base_state)

    assert result["risk_level"] == "low"


@pytest.mark.asyncio
async def test_risk_assessor_update_intent(base_state):
    """Test risk assessor for update intent."""
    base_state["intent"] = "update"
    base_state["cli_commands"] = ["set timer t3412 60"]

    agent = RiskAssessorAgent()
    result = await agent.execute(base_state)

    assert result["risk_level"] in ["low", "medium", "high", "critical"]
    assert result["impact_description"] is not None


@pytest.mark.asyncio
async def test_response_synthesizer_general(base_state):
    """Test response synthesizer for general intent."""
    base_state["intent"] = "general"
    base_state["user_query"] = "Hello"

    agent = ResponseSynthesizerAgent()
    result = await agent.execute(base_state)

    assert result["final_response"] != ""
    assert "vepc" in result["final_response"].lower() or "help" in result["final_response"].lower()
