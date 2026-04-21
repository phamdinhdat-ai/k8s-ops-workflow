# Usage Guide

## Quick Start

### Installation

```bash
# Clone and setup
cd k8s-ops-workflow
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials
```

### Basic Usage

```python
from workflows.main import run_workflow

# QUERY Mode - Simple pod listing
result = await run_workflow(
    user_query="Show me all pods in production",
    rca_mode=False,
    user_context={"namespace": "production"}
)

print(result["final_response"])
```

### RCA Mode

```python
# RCA Mode - Investigate incident
result = await run_workflow(
    user_query="Investigate payment-service outage",
    rca_mode=True,
    user_context={
        "namespace": "production",
        "service_name": "payment-service",
        "time_range": "2h",
        "error_description": "503 errors and high latency"
    }
)

print(result["final_response"])
```

## Use Cases

### 1. Read-Only Queries

**Check pod status:**
```python
await run_workflow(
    "What's the status of api-gateway pods?",
    user_context={"namespace": "production"}
)
```

**List deployments:**
```python
await run_workflow(
    "Show all deployments in staging",
    user_context={"namespace": "staging"}
)
```

**Check resource usage:**
```python
await run_workflow(
    "What's the CPU and memory usage in production?",
    user_context={"namespace": "production"}
)
```

### 2. Report Generation

**Health summary:**
```python
await run_workflow(
    "Generate health summary for production namespace",
    user_context={"namespace": "production"}
)
```

**Capacity report:**
```python
await run_workflow(
    "Create capacity overview report",
    user_context={"namespace": "production"}
)
```

**Deployment status:**
```python
await run_workflow(
    "Report on all deployment rollouts",
    user_context={"namespace": "production"}
)
```

### 3. Root Cause Analysis

**Full RCA workflow:**
```python
await run_workflow(
    "Investigate why payment-service is down",
    rca_mode=True,
    user_context={
        "namespace": "production",
        "service_name": "payment-service",
        "time_range": "1h"
    }
)
```

**Output includes:**
- Timeline of events
- Root cause hypothesis with confidence
- Impact assessment (severity, blast radius)
- Remediation steps with risk levels

## CLI Usage

```bash
# Run example workflows
python -m workflows.main

# With debug mode
DEBUG_MODE=true python -m workflows.main
```

## Docker Usage

```bash
# Build and run
docker-compose up --build

# Run specific query
docker-compose run k8s-ops-workflow python -c "
from workflows.main import run_workflow
import asyncio
result = asyncio.run(run_workflow('show pods'))
print(result['final_response'])
"
```

## Configuration

### Environment Variables

```bash
# Required
ANTHROPIC_API_KEY=your_key
ANTHROPIC_BASE_URL=https://ckey.vn

# Optional
DEFAULT_NAMESPACE=production
DEFAULT_CLUSTER=prod-cluster
KUBECONFIG=~/.kube/config
STREAMING_ENABLED=true
DEBUG_MODE=false
```

### User Context Fields

```python
user_context = {
    "namespace": "production",      # K8s namespace
    "cluster": "prod-cluster",      # Cluster name
    "service_name": "api-gateway",  # Service to investigate
    "time_range": "1h",             # Time window (1h, 30m, 2h)
    "error_description": "..."      # Optional error details
}
```

## Testing

```bash
# Run all tests
make test

# Run specific test
pytest tests/test_agents.py -v

# Run with coverage
pytest --cov=agents --cov=workflows tests/
```

## Troubleshooting

### Common Issues

**Missing namespace:**
- The workflow will prompt via HITL ContextGate
- Or provide in user_context

**kubectl access denied:**
- Ensure KUBECONFIG is set correctly
- Verify cluster access: `kubectl cluster-info`

**Empty responses:**
- Check ResponseValidator warnings in state["warnings"]
- Verify K8s resources exist in namespace

**Memory not persisting:**
- Check data/memory directory permissions
- Verify MemoryStore initialization
