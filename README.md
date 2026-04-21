# K8s Operations Workflow

Production-grade multi-agent workflow for Kubernetes operations engineers.

## Features

- **Read-Only Queries** — Live deployment state inspection
- **Root Cause Analysis (RCA)** — Deep investigation for service incidents
- **Report Generation** — Structured health/status reports

## Architecture

- **Intent-first**: Fast intent classification before agent execution
- **Mode-aware**: QUERY and RCA modes with explicit activation
- **Human-in-the-loop**: 4 defined gates for critical decisions
- **Evidence-driven**: Correlates K8s state + logs/traces + change events
- **Streaming-first**: Real-time token streaming for all responses

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
python -m workflows.main
```

## Project Structure

```
k8s-ops-workflow/
├── agents/          # 11 purpose-built agents
├── core/            # State, memory, base classes
├── workflows/       # LangGraph workflow definitions
├── tests/           # Unit and integration tests
└── config/          # Configuration files
```
