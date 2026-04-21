# Architecture Overview

## System Design

The K8s Operations Workflow is a production-grade multi-agent system built on LangGraph for Kubernetes operations engineers.

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Workflow Orchestrator                    │
│                        (LangGraph)                           │
└─────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                │                           │
        ┌───────▼────────┐         ┌───────▼────────┐
        │  QUERY Mode    │         │   RCA Mode     │
        │   Workflow     │         │   Workflow     │
        └───────┬────────┘         └───────┬────────┘
                │                           │
    ┌───────────┴───────────┐   ┌──────────┴──────────┐
    │                       │   │                     │
┌───▼────┐  ┌──────▼──────┐ │ ┌─▼──────┐  ┌────▼────┐
│ K8s    │  │ Knowledge   │ │ │Evidence│  │Timeline │
│ State  │  │ Retriever   │ │ │Collect │  │ Builder │
└────────┘  └─────────────┘ │ └────────┘  └─────────┘
                            │
                    ┌───────▼────────┐
                    │ Report         │
                    │ Generator      │
                    └────────────────┘
```

### Agent Registry

**Shared Agents (4)**
- ContextPreProcessor
- ResponseValidator
- MemoryWriter
- IntentClassifier (inline)

**QUERY Mode Agents (6)**
- K8sStateCollector
- KnowledgeRetriever
- ReportPlanner
- MetricsSummarizer
- ReportGenerator
- Formatter

**RCA Mode Agents (8)**
- LogTraceRetriever
- ChangeEventDetector
- TimelineBuilder
- ProblemDetector
- RootCauseAnalyzer
- ImpactAssessor
- RemediationPlanner
- RCAReportGenerator

### State Management

The workflow uses a comprehensive state object (`OperationState`) that tracks:
- User input and context
- Intent classification results
- Collected evidence (K8s state, logs, metrics)
- Analysis results (problems, root cause, impact)
- HITL gates and responses
- Memory and conversation history
- Errors and warnings

### Data Flow

1. **Input** → User query + context
2. **Preprocessing** → Context enrichment from memory
3. **Classification** → Intent detection
4. **Routing** → Mode-specific workflow
5. **Collection** → Evidence gathering
6. **Analysis** → Problem detection + RCA
7. **Output** → Formatted response
8. **Memory** → Persist findings

### HITL Gates

Four human-in-the-loop checkpoints:
1. **ContextGate** - Missing namespace/service
2. **CLIAccessGate** - Kubectl permission confirmation
3. **RCAConfirmGate** - Review findings before deep analysis
4. **ReportScopeGate** - Confirm complex report scope

### Memory System

Persistent storage for:
- Session context (namespace, cluster preferences)
- Conversation history (last 3 turns)
- RCA findings (7-day retention)
- Recurring incident detection

## Technology Stack

- **Orchestration**: LangGraph
- **LLM**: Anthropic Claude (via custom base URL)
- **K8s Access**: kubectl via MCP
- **Vector DB**: ChromaDB (for logs/traces)
- **State**: TypedDict with full type safety
- **Testing**: pytest + pytest-asyncio

## Deployment

- Docker containerized
- Docker Compose for local dev
- Kubernetes-ready (can run in-cluster)
- Environment-based configuration
