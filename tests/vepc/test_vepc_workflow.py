"""Tests for vEPC workflow."""
import pytest
from workflows.vepc.vepc_workflow import run_vepc_workflow, build_vepc_workflow


@pytest.mark.asyncio
async def test_vepc_workflow_show_query():
    """Test vEPC workflow with show query."""
    result = await run_vepc_workflow(
        user_query="Show me the current MCC and MNC",
        language="en"
    )

    assert result["final_response"] != ""
    assert result["intent"] == "show"
    assert len(result["cli_commands"]) > 0


@pytest.mark.asyncio
async def test_vepc_workflow_update_query():
    """Test vEPC workflow with update query."""
    result = await run_vepc_workflow(
        user_query="Set timer T3412 to 60 minutes",
        language="en"
    )

    assert result["final_response"] != ""
    assert result["intent"] == "update"
    assert result["risk_level"] in ["low", "medium", "high", "critical"]


@pytest.mark.asyncio
async def test_vepc_workflow_explain_query():
    """Test vEPC workflow with explain query."""
    result = await run_vepc_workflow(
        user_query="What does the T3412 timer do?",
        language="en"
    )

    assert result["final_response"] != ""
    assert result["intent"] == "explain"


@pytest.mark.asyncio
async def test_vepc_workflow_general_query():
    """Test vEPC workflow with general query."""
    result = await run_vepc_workflow(
        user_query="Hello",
        language="en"
    )

    assert result["final_response"] != ""
    assert result["intent"] == "general"


@pytest.mark.asyncio
async def test_vepc_workflow_vietnamese():
    """Test vEPC workflow with Vietnamese query."""
    result = await run_vepc_workflow(
        user_query="Xin chào",
        language="vi"
    )

    assert result["final_response"] != ""
    assert "xin chào" in result["final_response"].lower() or "chào" in result["final_response"].lower()


@pytest.mark.asyncio
async def test_vepc_workflow_with_conversation_history():
    """Test vEPC workflow with conversation history."""
    history = [
        {
            "user": "Set timer T3412 to 60 minutes",
            "assistant": "Command: set timer t3412 60",
        }
    ]

    result = await run_vepc_workflow(
        user_query="change it to 90",
        language="en",
        conversation_history=history
    )

    assert result["final_response"] != ""


@pytest.mark.asyncio
async def test_build_vepc_workflow():
    """Test building vEPC workflow graph."""
    workflow = build_vepc_workflow()
    assert workflow is not None
