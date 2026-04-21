# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Multi-agent operations workflow system with two distinct workflows:

### K8s Operations Workflow
Production-grade multi-agent system for Kubernetes operations engineers with two modes:
- **QUERY Mode**: Read-only queries for live deployment state inspection and report generation
- **RCA Mode**: Deep root cause analysis for service incidents with evidence correlation

### vEPC Operations Workflow
AI-powered assistant for telecom engineers working with virtual Evolved Packet Core (vEPC) systems:
- **Natural Language CLI**: Translates English/Vietnamese queries into validated vEPC CLI commands
- **Configuration Management**: Show and update vEPC configuration with automatic validation
- **Knowledge Base**: Explains vEPC concepts and provides troubleshooting guidance
- **Risk Assessment**: Automatic risk evaluation for configuration changes (warns but never blocks)

## Development Commands

### Setup
```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env with ANTHROPIC_API_KEY and ANTHROPIC_BASE_URL
```

### Running
```bash
# K8s workflow
make run              # Run K8s workflow
make dev              # Run K8s workflow with debug mode
python -m workflows.main  # Direct execution

# vEPC workflow
make run-vepc         # Run vEPC workflow examples
make dev-vepc         # Run vEPC workflow
python -m workflows.vepc.main  # Direct execution
```

### Testing
```bash
make test             # Run all tests with pytest
pytest tests/test_agents.py -v  # Run specific test file
pytest tests/test_workflows.py::test_name -v  # Run single test
pytest --cov=agents --cov=workflows tests/  # Run with coverage
```

### Code Quality
```bash
make lint             # Check with ruff
make format           # Format with black (line-length=100)
make clean            # Remove __pycache__ and test artifacts
```

### Docker
```bash
docker-compose up --build
docker-compose run k8s-ops-workflow python -m workflows.main
```

## Architecture

### Workflow Orchestration
The system uses LangGraph to orchestrate multiple workflow graphs:

**K8s Workflows:**

1. **query_workflow.py**: Handles read-only queries and report generation
   - Entry: `preprocess_context` → `classify_intent` → conditional routing
   - Routes: `query_k8s`, `query_knowledge`, or `report` based on intent
   - Exit: `format_response` → `write_memory` → END

2. **rca_workflow.py**: Handles root cause analysis investigations
   - Entry: `preprocess_context` → `rca_intake` → evidence collection pipeline
   - Pipeline: K8s state → logs/traces → change events → timeline → problem detection → root cause analysis → impact assessment → remediation planning
   - Exit: `generate_rca_report` → `write_memory` → END

**vEPC Workflow:**

3. **vepc/vepc_workflow.py**: Handles vEPC CLI generation and knowledge queries
   - Entry: `rewrite_query` → `classify_intent` → `retrieve_knowledge` → conditional routing
   - CLI path (show/update): `generate_cli` → `validate_cli` (with retry loop) → `assess_risk` (update only) → `synthesize_response`
   - Knowledge path (explain/troubleshoot/general): direct to `synthesize_response`
   - Exit: `synthesize_response` → END
   - Key feature: CLI validation retry loop (up to 2 retries) feeds errors back to CLI generator

### State Management

**K8s State:**
All K8s workflow state is tracked in `OperationState` (TypedDict in `core/state.py`). Key state fields:
- Input: `user_query`, `user_context`, `rca_mode`
- Classification: `intent`, `intent_confidence`, `intent_entities`
- HITL: `hitl_pending`, `hitl_question`, `hitl_response`, `hitl_gate`
- Evidence: `k8s_state`, `log_trace_evidence`, `change_events`, `metrics_summary`
- Analysis: `timeline`, `detected_problems`, `root_cause`, `impact_assessment`, `remediation_suggestions`
- Output: `final_response`, `report_structure`, `warnings`, `errors`

**vEPC State:**
All vEPC workflow state is tracked in `VEPCState` (TypedDict in `core/vepc_state.py`). Key state fields:
- Input: `user_query`, `language` (en/vi), `conversation_history`
- Query processing: `rewritten_query`, `rewrite_reasoning`
- Classification: `intent` (show/update/explain/troubleshoot/general), `intent_confidence`, `intent_entities`
- Knowledge: `knowledge_results`, `knowledge_context`
- CLI: `cli_commands`, `cli_explanation`, `cli_generation_reasoning`
- Validation: `validation_attempts`, `validation_passed`, `validation_errors`, `validation_warnings`
- Risk: `risk_level` (low/medium/high/critical), `risk_warnings`, `impact_description`, `affected_components`
- Output: `final_response`, `response_metadata`

### Agent System
Agents are in `agents/` directory:

**K8s agents** (inherit from `BaseAgent` in `core/base_agent.py`):

**Shared agents** (used in both K8s modes):
- `ContextPreProcessorAgent`: Enriches user context from memory
- `ResponseValidatorAgent`: Validates output completeness
- `MemoryWriterAgent`: Persists findings to memory store

**QUERY mode agents**:
- `ReportPlannerAgent`: Plans report structure
- `MetricsSummarizer`: Aggregates metrics data

**RCA mode agents**:
- `LogTraceRetrieverAgent`: Retrieves logs/traces from vector DB
- `ChangeEventDetectorAgent`: Detects deployment/config changes
- `TimelineBuilderAgent`: Constructs event timeline
- `ImpactAssessorAgent`: Assesses incident impact and blast radius

**vEPC agents** (in `agents/vepc/`, inherit from `VEPCBaseAgent` in `core/vepc_base_agent.py`):
- `QueryRewriterAgent`: Resolves ambiguous/follow-up queries using conversation context
- `IntentClassifierAgent`: Classifies intent (show/update/explain/troubleshoot/general)
- `KnowledgeRetrieverAgent`: Retrieves vEPC documentation from ChromaDB vector database
- `CLIGeneratorAgent`: Generates vEPC CLI commands from natural language
- `CLIValidatorAgent`: Validates CLI syntax (used in retry loop)
- `RiskAssessorAgent`: Assesses risk level for configuration changes
- `ResponseSynthesizerAgent`: Combines knowledge, CLI, and risk into final response

### Memory System
`MemoryStore` in `core/memory.py` provides persistent storage:
- Session context (namespace, cluster preferences)
- Conversation history (last 3 turns)
- RCA findings (7-day retention)
- Stored in `data/memory/` directory

Note: vEPC workflow uses conversation history passed as parameter, not the K8s MemoryStore.

### HITL Gates
Four human-in-the-loop checkpoints trigger `hitl_pending=True`:
1. **ContextGate**: Missing required context (namespace/service)
2. **CLIAccessGate**: Kubectl permission confirmation
3. **RCAConfirmGate**: Review findings before deep analysis
4. **ReportScopeGate**: Confirm complex report scope

## Configuration

### Environment Variables (.env)
Required:
- `ANTHROPIC_API_KEY`: API key for Claude
- `ANTHROPIC_BASE_URL`: API endpoint (default: https://api.anthropic.com)

**K8s-specific:**
- `KUBECONFIG`: Path to kubeconfig (default: ~/.kube/config)
- `DEFAULT_NAMESPACE`: Default K8s namespace (default: default)
- `DEFAULT_CLUSTER`: Default cluster name (default: production)
- `VECTORDB_PATH`: ChromaDB storage path (default: ./data/vectordb)
- `STREAMING_ENABLED`: Enable token streaming (default: true)
- `DEBUG_MODE`: Enable debug logging (default: false)
- `MAX_RETRIES`: Retry attempts for API calls (default: 3)
- `TIMEOUT_SECONDS`: Workflow timeout (default: 300)

**vEPC-specific:**
- `VEPC_VECTORDB_PATH`: ChromaDB storage for vEPC docs (default: ./data/vepc_vectordb)
- `VEPC_VECTORDB_COLLECTION`: Collection name (default: vepc_docs)
- `VEPC_MAX_VALIDATION_RETRIES`: CLI validation retry limit (default: 2)
- `VEPC_CLI_TIMEOUT`: CLI operation timeout (default: 30)
- `VEPC_STREAMING_ENABLED`: Enable streaming (default: true)
- `VEPC_DEBUG_MODE`: Enable debug logging (default: false)

### Code Style
- Python 3.11+
- Black formatter with line-length=100
- Ruff linter with line-length=100
- Type hints required (TypedDict for state)
- Async/await for all agent execution

## Testing Strategy

Tests are in `tests/` directory:

**K8s tests:**
- `test_agents.py`: Unit tests for K8s agents
- `test_workflows.py`: Integration tests for K8s workflow graphs

**vEPC tests:**
- `vepc/test_vepc_agents.py`: Unit tests for vEPC agents
- `vepc/test_vepc_workflow.py`: Integration tests for vEPC workflow

All tests use `pytest-asyncio` for async test functions and mock external dependencies (K8s API, Anthropic API, ChromaDB).

## Key Implementation Details

### Adding New K8s Agents
1. Create agent class in `agents/` inheriting from `BaseAgent`
2. Implement `execute(state: OperationState) -> OperationState` method
3. Register in `agents/__init__.py`
4. Add node to workflow graph in `workflows/query_workflow.py` or `workflows/rca_workflow.py`
5. Add unit tests in `tests/test_agents.py`

### Adding New vEPC Agents
1. Create agent class in `agents/vepc/` inheriting from `VEPCBaseAgent`
2. Implement `execute(state: VEPCState) -> VEPCState` method
3. Register in `agents/vepc/__init__.py`
4. Add node to workflow graph in `workflows/vepc/vepc_workflow.py`
5. Add unit tests in `tests/vepc/test_vepc_agents.py`

### Modifying Workflow Logic
- Workflow graphs are defined using LangGraph's `StateGraph`
- Nodes are functions that take `OperationState` and return `OperationState`
- Use `add_conditional_edges` for routing based on state
- Always update state immutably (return new dict, don't mutate in place)

### Working with K8s
- K8s access is via kubectl (assumes KUBECONFIG is configured)
- Use MCP (Model Context Protocol) for kubectl commands
- All K8s operations are read-only (no mutations)
- Namespace is required for most operations (enforced by ContextGate)

### Vector DB for Logs
- ChromaDB stores logs/traces for semantic search
- Collection name: `k8s_logs` (configurable via VECTORDB_COLLECTION)
- Embeddings via sentence-transformers
- Used only in RCA mode for log retrieval

### Vector DB for vEPC Documentation
- ChromaDB stores vEPC documentation for knowledge retrieval
- Collection name: `vepc_docs` (configurable via VEPC_VECTORDB_COLLECTION)
- Embeddings via sentence-transformers
- Used in all vEPC intents except "general"
- Documents should include metadata (source, page, section) for better context

### vEPC CLI Validation Retry Logic
- When CLI validation fails, the workflow loops back to CLI generation
- Validation errors are passed to the CLI generator for correction
- Maximum 2 retries (configurable via VEPC_MAX_VALIDATION_RETRIES)
- After max retries, workflow proceeds to synthesis with errors included
- This targeted retry avoids restarting the entire workflow

### vEPC Risk Assessment
- Only runs for "update" intent (skipped for show/explain/troubleshoot/general)
- Risk levels: low, medium, high, critical
- Based on keywords, parameters, and impact analysis
- Warnings are informational only - never blocks operations
- Respects engineering autonomy while providing safety information
