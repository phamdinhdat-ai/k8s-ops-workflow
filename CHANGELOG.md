# Changelog

## [1.0.0] - 2026-04-21

### Added

**Core Infrastructure**
- Complete state management system with 40+ typed fields
- Memory store for session persistence and RCA history
- Base agent class with standardized error handling
- Configuration management with environment variables

**New Agents (9)**
- ContextPreProcessorAgent: Enriches context from memory and query parsing
- ResponseValidatorAgent: Validates response quality and detects hallucinations
- MemoryWriterAgent: Persists session context and RCA findings
- ReportPlannerAgent: Structures report scope and template selection
- MetricsSummarizerAgent: Collects CPU/memory/restart metrics
- LogTraceRetrieverAgent: Time-bounded log and trace queries
- ChangeEventDetectorAgent: Detects and correlates recent K8s changes
- TimelineBuilderAgent: Merges evidence into chronological timeline
- ImpactAssessorAgent: Assesses blast radius and severity (SEV1-4)

**Workflows**
- QUERY mode workflow with 7-8 node execution path
- RCA mode workflow with 14-15 node execution path
- Intent-based conditional routing
- 4 HITL gate definitions (ContextGate, CLIAccessGate, RCAConfirmGate, ReportScopeGate)

**Documentation**
- Comprehensive README with quick start guide
- USAGE guide with code examples for all use cases
- ARCHITECTURE overview with system design diagrams
- PROJECT_SUMMARY with implementation status

**DevOps**
- Dockerfile for containerization
- docker-compose.yml for local development
- Makefile with common tasks (test, lint, format, run)
- pytest configuration with async support
- VSCode settings and launch configurations

**Testing**
- Unit tests for agents
- Integration tests for workflows
- Test fixtures and helpers

### Design Principles

- Intent-first classification before agent execution
- Mode-aware routing (QUERY vs RCA)
- Human-in-the-loop gates at critical decision points
- Evidence-driven RCA with timeline correlation
- Minimal agent chains with conditional routing
- Fail-safe error handling in all agents
- Full audit trail via agent_responses tracking
- Streaming-first architecture (ready for astream_events)

### Technical Stack

- LangGraph for workflow orchestration
- Anthropic Claude via custom base URL
- TypedDict for type-safe state management
- ChromaDB for vector storage (integration ready)
- Kubernetes Python client (integration ready)
- pytest + pytest-asyncio for testing

### Known Limitations

- K8s state collection uses placeholder data (needs MCP integration)
- VectorDB queries return empty results (needs ChromaDB connection)
- HITL gates defined but not yet interactive (needs UI)
- Intent classifier uses simple keyword matching (needs LLM)
- Streaming not yet implemented (structure ready)

### Next Steps

See PROJECT_SUMMARY.md for production integration roadmap.
