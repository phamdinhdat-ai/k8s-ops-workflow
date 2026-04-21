"""Integration tests for workflows."""
import pytest
from workflows.main import create_initial_state, run_workflow


def test_initial_state_creation():
    """Test initial state creation."""
    state = create_initial_state("test query", rca_mode=False)
    
    assert state["user_query"] == "test query"
    assert state["workflow_mode"] == "QUERY"
    assert state["rca_mode"] is False
    assert len(state["errors"]) == 0


def test_rca_initial_state():
    """Test RCA mode initial state."""
    state = create_initial_state("investigate issue", rca_mode=True)
    
    assert state["workflow_mode"] == "RCA"
    assert state["rca_mode"] is True


@pytest.mark.asyncio
async def test_query_workflow_execution():
    """Test QUERY workflow execution."""
    result = await run_workflow(
        user_query="show pods",
        rca_mode=False,
        user_context={"namespace": "default"}
    )
    
    assert result is not None
    assert "final_response" in result
    assert result["workflow_mode"] == "QUERY"
