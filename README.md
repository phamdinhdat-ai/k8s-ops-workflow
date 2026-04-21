# Multi-Agent Operations Workflow

Production-grade multi-agent workflows for operations engineers.

## Workflows

### K8s Operations Workflow
- **Read-Only Queries** — Live deployment state inspection
- **Root Cause Analysis (RCA)** — Deep investigation for service incidents
- **Report Generation** — Structured health/status reports

### vEPC Operations Workflow
- **Natural Language CLI** — Generate vEPC CLI commands from plain English or Vietnamese
- **Configuration Management** — Show and update vEPC configuration with validation
- **Knowledge Base** — Explain vEPC concepts and troubleshoot issues
- **Risk Assessment** — Automatic risk evaluation for configuration changes

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

# Run K8s workflow
python -m workflows.main

# Run vEPC workflow
python -m workflows.vepc.main
```

## Project Structure

```
k8s-ops-workflow/
├── agents/
│   ├── (k8s agents)     # K8s-specific agents
│   └── vepc/            # vEPC-specific agents
├── core/                # State, memory, base classes
├── workflows/
│   ├── (k8s workflows)  # K8s workflow definitions
│   └── vepc/            # vEPC workflow definitions
├── tests/
│   ├── (k8s tests)      # K8s tests
│   └── vepc/            # vEPC tests
└── config/
    ├── (k8s config)     # K8s configuration
    └── vepc/            # vEPC configuration
```
