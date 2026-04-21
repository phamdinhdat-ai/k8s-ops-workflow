# Multi-Agent Operations Workflow - Project Summary

## Overview

This repository contains two production-grade multi-agent workflows built on LangGraph:

1. **K8s Operations Workflow** - For Kubernetes operations engineers
2. **vEPC Operations Workflow** - For telecom engineers working with virtual Evolved Packet Core systems

Both workflows run in parallel, sharing infrastructure while maintaining separate agent systems and state management.

## Project Structure

```
k8s-ops-workflow/
├── agents/
│   ├── (K8s agents)              # K8s-specific agents
│   └── vepc/                     # vEPC-specific agents (7 agents)
│       ├── query_rewriter_agent.py
│       ├── intent_classifier_agent.py
│       ├── knowledge_retriever_agent.py
│       ├── cli_generator_agent.py
│       ├── cli_validator_agent.py
│       ├── risk_assessor_agent.py
│       └── response_synthesizer_agent.py
├── core/
│   ├── state.py                  # K8s state definition
│   ├── vepc_state.py             # vEPC state definition
│   ├── base_agent.py             # K8s base agent
│   ├── vepc_base_agent.py        # vEPC base agent
│   └── memory.py                 # K8s memory store
├── workflows/
│   ├── query_workflow.py         # K8s QUERY mode
│   ├── rca_workflow.py           # K8s RCA mode
│   ├── main.py                   # K8s entry point
│   └── vepc/                     # vEPC workflow
│       ├── vepc_workflow.py      # vEPC workflow graph
│       └── main.py               # vEPC entry point
├── config/
│   ├── templates.yaml            # K8s templates
│   ├── settings.py               # K8s settings
│   ├── vepc_settings.py          # vEPC settings
│   └── vepc/
│       └── templates.yaml        # vEPC templates
├── tests/
│   ├── test_agents.py            # K8s agent tests
│   ├── test_workflows.py         # K8s workflow tests
│   └── vepc/                     # vEPC tests
│       ├── test_vepc_agents.py
│       └── test_vepc_workflow.py
├── examples/
│   ├── vepc_quickstart.py        # vEPC usage examples
│   └── populate_vepc_docs.py     # Load vEPC documentation
└── docs/
    ├── README.md                 # Main readme
    ├── CLAUDE.md                 # Development guide
    ├── USAGE.md                  # K8s usage guide
    ├── VEPC_USAGE.md             # vEPC usage guide
    ├── ARCHITECTURE.md           # K8s architecture
    ├── VEPC_ARCHITECTURE.md      # vEPC architecture
    └── VEPC_QUICKREF.md          # vEPC quick reference
```

## Quick Start

### Installation
```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your ANTHROPIC_API_KEY
```

### Run K8s Workflow
```bash
make run
# or
python -m workflows.main
```

### Run vEPC Workflow
```bash
# First, populate the knowledge base
python examples/populate_vepc_docs.py

# Then run examples
make run-vepc
# or
python -m workflows.vepc.main
```

## vEPC Workflow Features

### Natural Language CLI Generation
- Translates English or Vietnamese queries into validated vEPC CLI commands
- Example: "Set timer T3412 to 60 minutes" → `set timer t3412 60`

### Automatic Validation
- CLI syntax validation with up to 2 retries
- Errors fed back to generator for correction
- Prevents invalid commands from reaching the system

### Risk Assessment
- Automatic risk evaluation for configuration changes
- Risk levels: low, medium, high, critical
- Warns but never blocks operations (respects engineering autonomy)

### Knowledge Base
- Explains vEPC concepts (timers, features, protocols)
- Provides troubleshooting guidance
- Retrieves from ChromaDB vector database

### Multilingual Support
- Native English and Vietnamese support
- Localized responses and risk warnings
- Conversation context maintained across languages

## vEPC Workflow Pipeline

```
User Query (EN/VI)
    ↓
Query Rewriting (resolves follow-ups)
    ↓
Intent Classification (show/update/explain/troubleshoot/general)
    ↓
Knowledge Retrieval (from vEPC docs)
    ↓
[CLI Path] CLI Generation → Validation (retry loop) → Risk Assessment
    ↓
Response Synthesis
    ↓
Final Response
```

## Intent Types

| Intent | Description | CLI Generated | Risk Assessment |
|--------|-------------|---------------|-----------------|
| show | View configuration | Yes | No (read-only) |
| update | Modify configuration | Yes | Yes |
| explain | Understand concepts | No | No |
| troubleshoot | Diagnose issues | No | No |
| general | Greetings, thanks | No | No |

## Technology Stack

- **Orchestration**: LangGraph
- **LLM**: Anthropic Claude Sonnet 4.6
- **Vector DB**: ChromaDB with sentence-transformers
- **State Management**: TypedDict with full type safety
- **Testing**: pytest + pytest-asyncio
- **Language**: Python 3.11+

## Testing

```bash
# Test K8s workflow
pytest tests/test_agents.py tests/test_workflows.py -v

# Test vEPC workflow
pytest tests/vepc/ -v

# All tests with coverage
pytest --cov=agents --cov=workflows --cov=core tests/
```

## Configuration

### Required Environment Variables
```bash
ANTHROPIC_API_KEY=your_key
ANTHROPIC_BASE_URL=https://api.anthropic.com
```

### K8s-Specific
```bash
KUBECONFIG=~/.kube/config
DEFAULT_NAMESPACE=default
VECTORDB_PATH=./data/vectordb
```

### vEPC-Specific
```bash
VEPC_VECTORDB_PATH=./data/vepc_vectordb
VEPC_VECTORDB_COLLECTION=vepc_docs
VEPC_MAX_VALIDATION_RETRIES=2
```

## Documentation

- **CLAUDE.md** - Complete development guide for both workflows
- **VEPC_USAGE.md** - Detailed vEPC usage guide with examples
- **VEPC_ARCHITECTURE.md** - vEPC system design and data flow
- **VEPC_QUICKREF.md** - Quick reference for common tasks

## Key Design Principles

### vEPC Workflow
1. **Safety without blocking** - Risk warnings inform but don't prevent
2. **Targeted retries** - Validation errors fed back to CLI generator only
3. **Agent specialization** - Each agent has single, focused responsibility
4. **Stateful conversation** - Context maintained across turns
5. **Multilingual native** - English and Vietnamese as first-class citizens

## Next Steps

1. Populate vEPC knowledge base: `python examples/populate_vepc_docs.py`
2. Run examples: `python examples/vepc_quickstart.py`
3. Integrate with your vEPC system
4. Add more vEPC documentation to vector database
5. Customize CLI patterns and risk rules in `config/vepc/templates.yaml`

## License

See LICENSE file for details.
