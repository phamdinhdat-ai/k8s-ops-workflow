# vEPC Workflow - Quick Reference

## Installation

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your ANTHROPIC_API_KEY
```

## Populate Knowledge Base

```bash
python examples/populate_vepc_docs.py
```

## Run Examples

```bash
python examples/vepc_quickstart.py
```

## Basic Usage

```python
from workflows.vepc import run_vepc_workflow
import asyncio

# Show configuration
result = await run_vepc_workflow(
    user_query="Show me the current MCC and MNC",
    language="en"
)

# Update configuration
result = await run_vepc_workflow(
    user_query="Set timer T3412 to 60 minutes",
    language="en"
)

# Explain concept
result = await run_vepc_workflow(
    user_query="What does CSFB mean?",
    language="en"
)

# Vietnamese
result = await run_vepc_workflow(
    user_query="Hiển thị cấu hình MME",
    language="vi"
)
```

## Intent Types

| Intent | Description | Example |
|--------|-------------|---------|
| `show` | View configuration | "Show me the current MCC" |
| `update` | Modify configuration | "Set timer T3412 to 60" |
| `explain` | Understand concepts | "What does T3412 do?" |
| `troubleshoot` | Diagnose issues | "Attach is failing" |
| `general` | Greetings, thanks | "Hello" |

## Risk Levels

- **low**: Read-only operations
- **medium**: Configuration changes
- **high**: Operations affecting sessions
- **critical**: Service outage risk

## CLI Validation

- Automatic syntax validation
- Up to 2 retries on failure
- Errors fed back to generator

## Response Structure

```python
{
    "final_response": "...",
    "intent": "show",
    "cli_commands": ["show mcc"],
    "risk_level": "low",
    "validation_passed": true,
    "metadata": {...}
}
```

## Conversation Context

```python
history = [
    {
        "user": "Set timer T3412 to 60",
        "assistant": "Command: set timer t3412 60"
    }
]

result = await run_vepc_workflow(
    user_query="change it to 90",
    language="en",
    conversation_history=history
)
```

## Environment Variables

```bash
# Required
ANTHROPIC_API_KEY=your_key
ANTHROPIC_BASE_URL=https://api.anthropic.com

# Optional
VEPC_VECTORDB_PATH=./data/vepc_vectordb
VEPC_VECTORDB_COLLECTION=vepc_docs
VEPC_MAX_VALIDATION_RETRIES=2
VEPC_CLI_TIMEOUT=30
```

## Testing

```bash
# Run all vEPC tests
pytest tests/vepc/ -v

# Run specific test
pytest tests/vepc/test_vepc_agents.py -v

# With coverage
pytest --cov=agents.vepc --cov=workflows.vepc tests/vepc/
```

## Supported Parameters

### Network Identity
MCC, MNC, MME Code, MME GID, TAI, PLMN

### Timers
T3412, T3402, T3410, T3422, T3450, T3460, T3470

### Capacity
max_ue, max_bearers, max_sessions, pool_size

### Features
CSFB, SRVCC, VoLTE, Emergency Call, Roaming
