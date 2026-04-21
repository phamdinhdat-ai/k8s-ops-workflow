# vEPC Workflow Deployment Guide

## Prerequisites

- Python 3.11+
- Anthropic API key
- ChromaDB for vector storage
- (Optional) Docker for containerized deployment

## Local Deployment

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:
```bash
ANTHROPIC_API_KEY=your_api_key_here
ANTHROPIC_BASE_URL=https://api.anthropic.com

VEPC_VECTORDB_PATH=./data/vepc_vectordb
VEPC_VECTORDB_COLLECTION=vepc_docs
VEPC_MAX_VALIDATION_RETRIES=2
VEPC_CLI_TIMEOUT=30
VEPC_STREAMING_ENABLED=true
VEPC_DEBUG_MODE=false
```

### 3. Populate Knowledge Base

```bash
python examples/populate_vepc_docs.py
```

### 4. Run Tests

```bash
pytest tests/vepc/ -v
```

### 5. Start Application

```bash
python -m workflows.vepc.main
```

## Docker Deployment

### Build Image

```bash
docker build -t vepc-workflow .
```

### Run Container

```bash
docker run -d \
  --name vepc-workflow \
  -e ANTHROPIC_API_KEY=your_key \
  -v $(pwd)/data:/app/data \
  -p 8000:8000 \
  vepc-workflow
```

## Docker Compose

```yaml
version: '3.8'

services:
  vepc-workflow:
    build: .
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - VEPC_VECTORDB_PATH=/app/data/vepc_vectordb
    volumes:
      - ./data:/app/data
    ports:
      - "8000:8000"
```

Run:
```bash
docker-compose up -d
```

## Production Deployment

### Environment Variables

```bash
# Required
ANTHROPIC_API_KEY=prod_key
ANTHROPIC_BASE_URL=https://api.anthropic.com

# Vector DB
VEPC_VECTORDB_PATH=/var/lib/vepc/vectordb
VEPC_VECTORDB_COLLECTION=vepc_docs

# Performance
VEPC_MAX_VALIDATION_RETRIES=2
VEPC_CLI_TIMEOUT=30
VEPC_STREAMING_ENABLED=true

# Monitoring
VEPC_DEBUG_MODE=false
LOG_LEVEL=INFO
```

### Health Check

```python
@app.get("/health")
async def health_check():
    return {"status": "healthy", "workflow": "vepc"}
```

### Monitoring

- Log all queries and responses
- Track intent distribution
- Monitor validation failure rates
- Alert on high error rates

### Scaling

- Use Redis for session storage
- Deploy multiple instances behind load balancer
- Cache vector DB queries
- Implement rate limiting per user/session

## Troubleshooting

### Vector DB Issues

```bash
# Check vector DB
python -c "import chromadb; client = chromadb.Client(); print(client.list_collections())"
```

### API Connection

```bash
# Test Anthropic API
curl -H "x-api-key: $ANTHROPIC_API_KEY" \
     -H "anthropic-version: 2023-06-01" \
     $ANTHROPIC_BASE_URL/v1/messages
```

### Validation Failures

Check `config/vepc/templates.yaml` for correct CLI patterns and parameters.
