# vEPC Workflow Usage Guide

## Overview

The vEPC workflow is an AI-powered assistant for telecom engineers working with virtual Evolved Packet Core (vEPC) systems. It translates natural language queries (English or Vietnamese) into validated CLI commands with automatic risk assessment.

## Quick Start

```bash
# Run example queries
python -m workflows.vepc.main

# Or use programmatically
from workflows.vepc import run_vepc_workflow
import asyncio

result = asyncio.run(run_vepc_workflow(
    user_query="Show me the current MCC and MNC",
    language="en"
))
print(result['final_response'])
```

## Use Cases

### 1. Show Configuration (Read-Only)

**English:**
```python
result = await run_vepc_workflow(
    user_query="Show me the current MCC and MNC",
    language="en"
)
```

**Vietnamese:**
```python
result = await run_vepc_workflow(
    user_query="Hiển thị MCC và MNC hiện tại",
    language="vi"
)
```

### 2. Update Configuration (Write Operations)

**English:**
```python
result = await run_vepc_workflow(
    user_query="Set timer T3412 to 60 minutes",
    language="en"
)
# Includes automatic risk assessment
print(f"Risk Level: {result['risk_level']}")
```

**Vietnamese:**
```python
result = await run_vepc_workflow(
    user_query="Đặt timer T3412 là 60 phút",
    language="vi"
)
```

### 3. Explain Concepts

**English:**
```python
result = await run_vepc_workflow(
    user_query="What does the T3412 timer do?",
    language="en"
)
```

**Vietnamese:**
```python
result = await run_vepc_workflow(
    user_query="Timer T3412 dùng để làm gì?",
    language="vi"
)
```

### 4. Troubleshooting

**English:**
```python
result = await run_vepc_workflow(
    user_query="Attach is failing, how do I troubleshoot?",
    language="en"
)
```

**Vietnamese:**
```python
result = await run_vepc_workflow(
    user_query="Attach bị lỗi, làm sao khắc phục?",
    language="vi"
)
```

### 5. Conversation Context

The workflow maintains conversation history for follow-up queries:

```python
history = [
    {
        "user": "Set timer T3412 to 60 minutes",
        "assistant": "Command: set timer t3412 60"
    }
]

result = await run_vepc_workflow(
    user_query="now change it to 90",
    language="en",
    conversation_history=history
)
```

## Workflow Pipeline

```
User Query
    ↓
Query Rewriting (resolves ambiguous/follow-up queries)
    ↓
Intent Classification (show/update/explain/troubleshoot/general)
    ↓
Knowledge Retrieval (from vEPC documentation)
    ↓
[CLI Path] CLI Generation → Validation (up to 2 retries) → Risk Assessment
    ↓
Response Synthesis
    ↓
Final Response
```

## Intent Types

| Intent | Description | CLI Generated | Risk Assessment |
|--------|-------------|---------------|-----------------|
| **show** | View configuration | Yes | No (read-only) |
| **update** | Modify configuration | Yes | Yes |
| **explain** | Understand concepts | No | No |
| **troubleshoot** | Diagnose issues | No | No |
| **general** | Greetings, thanks | No | No |

## Risk Levels

| Level | Description | Examples |
|-------|-------------|----------|
| **low** | Read-only operations | show, display, get |
| **medium** | Configuration changes | modify MCC, update timer |
| **high** | Operations affecting sessions | restart, reload, clear |
| **critical** | Service outage risk | shutdown, disable, delete |

## Response Structure

```python
{
    "final_response": "Human-readable response with CLI and explanation",
    "intent": "show|update|explain|troubleshoot|general",
    "cli_commands": ["list of generated CLI commands"],
    "risk_level": "low|medium|high|critical",
    "validation_passed": true/false,
    "metadata": {
        "intent": "show",
        "language": "en",
        "has_cli": true,
        "risk_level": "low"
    }
}
```

## Configuration

### Environment Variables

```bash
# Required
ANTHROPIC_API_KEY=your_key
ANTHROPIC_BASE_URL=https://api.anthropic.com

# Optional
VEPC_VECTORDB_PATH=./data/vepc_vectordb
VEPC_VECTORDB_COLLECTION=vepc_docs
VEPC_MAX_VALIDATION_RETRIES=2
VEPC_CLI_TIMEOUT=30
VEPC_STREAMING_ENABLED=true
VEPC_DEBUG_MODE=false
```

### Adding vEPC Documentation

To populate the knowledge base:

```python
import chromadb
from chromadb.config import Settings

client = chromadb.Client(Settings(
    persist_directory="./data/vepc_vectordb",
    anonymized_telemetry=False
))

collection = client.get_or_create_collection("vepc_docs")

# Add documents
collection.add(
    documents=["T3412 is the periodic TAU timer..."],
    metadatas=[{"source": "vepc_manual.pdf", "page": 42}],
    ids=["doc1"]
)
```

## Testing

```bash
# Run all vEPC tests
pytest tests/vepc/ -v

# Run specific test
pytest tests/vepc/test_vepc_agents.py::test_intent_classifier_show -v

# Run with coverage
pytest --cov=agents.vepc --cov=workflows.vepc tests/vepc/
```

## Supported vEPC Parameters

### Network Identity
- MCC (Mobile Country Code)
- MNC (Mobile Network Code)
- MME Code
- MME GID
- TAI (Tracking Area Identity)
- PLMN (Public Land Mobile Network)

### Timers
- T3412 (Periodic TAU timer)
- T3402 (Attach retry timer)
- T3410 (Paging timer)
- T3422 (Detach timer)
- T3450, T3460, T3470 (EMM timers)

### Capacity
- max_ue (Maximum UE connections)
- max_bearers
- max_sessions
- pool_size

### Features
- CSFB (Circuit Switched Fallback)
- SRVCC (Single Radio Voice Call Continuity)
- VoLTE (Voice over LTE)
- Emergency Call
- Roaming

## Troubleshooting

### CLI Validation Failures

If CLI validation fails repeatedly:
1. Check that parameter names match the known parameters in `config/vepc/templates.yaml`
2. Verify CLI patterns are correct
3. Review validation errors in the response

### Empty Knowledge Responses

If explanations are generic:
1. Ensure vEPC documentation is loaded into the vector database
2. Check `VEPC_VECTORDB_PATH` and `VEPC_VECTORDB_COLLECTION` settings
3. Verify ChromaDB is initialized correctly

### Language Detection Issues

The workflow uses the `language` parameter explicitly:
- Always pass `language="en"` or `language="vi"`
- Don't rely on automatic detection from query text
