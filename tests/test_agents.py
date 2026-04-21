"""Unit tests for agents."""
import pytest
from core.memory import MemoryStore
from agents import ContextPreProcessorAgent, ResponseValidatorAgent


@pytest.mark.asyncio
async def test_context_preprocessor():
    """Test context preprocessing."""
    memory = MemoryStore(storage_path="./test_data/memory")
    agent = ContextPreProcessorAgent(memory)
    
    state = {
        "session_id": "test-123",
        "user_query": "show pods in production",
        "user_context": {},
        "conversation_history": [],
        "agent_responses": [],
        "errors": [],
        "warnings": []
    }
    
    result = await agent.execute(state)
    
    assert result["user_context"].get("namespace") == "production"
    assert result["context_enriched"] is True


@pytest.mark.asyncio
async def test_response_validator():
    """Test response validation."""
    agent = ResponseValidatorAgent()
    
    state = {
        "k8s_state": {"pods": {"items": []}},
        "intent": "QUERY_K8S_STATE",
        "intent_entities": {},
        "agent_responses": [],
        "errors": [],
        "warnings": []
    }
    
    result = await agent.execute(state)
    
    assert "validation_result" in result
    assert result["validation_result"]["valid"] is True
