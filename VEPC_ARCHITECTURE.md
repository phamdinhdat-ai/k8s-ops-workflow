# vEPC Workflow Architecture

## System Design

The vEPC Operations Workflow is an AI-powered assistant for telecom engineers working with virtual Evolved Packet Core (vEPC) systems. It translates natural language queries in English or Vietnamese into validated CLI commands with automatic risk assessment.

## Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                  vEPC Workflow Orchestrator                  │
│                        (LangGraph)                           │
└─────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                │                           │
        ┌───────▼────────┐         ┌───────▼────────┐
        │ Query Rewriter │         │    Intent      │
        │                │────────▶│  Classifier    │
        └────────────────┘         └───────┬────────┘
                                           │
                                   ┌───────▼────────┐
                                   │   Knowledge    │
                                   │   Retriever    │
                                   └───────┬────────┘
                                           │
                        ┌──────────────────┴──────────────────┐
                        │                                     │
                ┌───────▼────────┐                   ┌───────▼────────┐
                │  CLI Generator │                   │   Response     │
                └───────┬────────┘                   │  Synthesizer   │
                        │                            └────────────────┘
                ┌───────▼────────┐
                │ CLI Validator  │
                └───────┬────────┘
                        │
                ┌───────▼────────┐
                │ Risk Assessor  │
                └───────┬────────┘
                        │
                ┌───────▼────────┐
                │   Response     │
                │  Synthesizer   │
                └────────────────┘
```

## Agent Pipeline

### 1. Query Rewriter
- **Purpose**: Resolves ambiguous or follow-up queries using conversation context
- **Input**: User query + conversation history
- **Output**: Standalone, unambiguous query
- **Example**: "change it to 90" → "Set timer T3412 to 90 minutes"

### 2. Intent Classifier
- **Purpose**: Identifies user intent from query
- **Intents**: show, update, explain, troubleshoot, general
- **Output**: Intent + confidence + extracted entities
- **Model**: Claude Sonnet 4.6 with temperature=0.1

### 3. Knowledge Retriever
- **Purpose**: Retrieves relevant vEPC documentation
- **Source**: ChromaDB vector database
- **Skipped for**: General intents (greetings, thanks)
- **Top-k**: 3 documents per query

### 4. CLI Generator (show/update intents only)
- **Purpose**: Generates vEPC CLI commands from natural language
- **Input**: Intent + entities + knowledge context
- **Output**: CLI command(s) + explanation
- **Model**: Claude Sonnet 4.6 with temperature=0.2

### 5. CLI Validator (CLI path only)
- **Purpose**: Validates CLI syntax
- **Retry logic**: Up to 2 retries on failure
- **Feedback loop**: Errors fed back to CLI Generator
- **Model**: Claude Sonnet 4.6 with temperature=0.0

### 6. Risk Assessor (update intent only)
- **Purpose**: Assesses operational risk of configuration changes
- **Risk levels**: low, medium, high, critical
- **Behavior**: Warns but never blocks
- **Model**: Claude Sonnet 4.6 with temperature=0.1

### 7. Response Synthesizer
- **Purpose**: Combines all information into final response
- **Inputs**: Knowledge context + CLI + risk warnings
- **Output**: Human-readable response in target language
- **Model**: Claude Sonnet 4.6 with temperature=0.3

## Data Flow

```
User Query (EN/VI)
        ↓
Query Rewriting ← Conversation History
        ↓
Intent Classification → {show, update, explain, troubleshoot, general}
        ↓
Knowledge Retrieval ← vEPC Documentation (ChromaDB)
        ↓
    ┌───┴───┐
    │       │
CLI Path    Knowledge Path
    │       │
    ├─ CLI Generation
    ├─ CLI Validation (retry loop)
    ├─ Risk Assessment (update only)
    │       │
    └───┬───┘
        ↓
Response Synthesis
        ↓
Final Response
```

## State Management

The workflow uses `VEPCState` (TypedDict) that tracks:

**Input:**
- user_query, language, conversation_history

**Processing:**
- rewritten_query, intent, intent_entities

**Knowledge:**
- knowledge_results, knowledge_context

**CLI:**
- cli_commands, cli_explanation, validation_passed, validation_errors

**Risk:**
- risk_level, risk_warnings, impact_description, affected_components

**Output:**
- final_response, response_metadata

## Conditional Routing

### After Intent Classification
```python
if intent in ["show", "update"]:
    → CLI Generation path
else:  # explain, troubleshoot, general
    → Direct to Response Synthesis
```

### After CLI Validation
```python
if validation_passed:
    if intent == "update":
        → Risk Assessment
    else:
        → Response Synthesis
elif validation_attempts < MAX_RETRIES:
    → Retry CLI Generation (with error feedback)
else:
    → Response Synthesis (with errors)
```

## Technology Stack

- **Orchestration**: LangGraph
- **LLM**: Anthropic Claude Sonnet 4.6
- **Vector DB**: ChromaDB with sentence-transformers
- **State**: TypedDict with full type safety
- **Testing**: pytest + pytest-asyncio
- **Languages**: Python 3.11+

## Design Principles

### 1. Safety Without Blocking
- Risk assessment warns engineers but never prevents operations
- Respects engineering autonomy
- Provides information for informed decisions

### 2. Targeted Retries
- CLI validation errors fed back specifically to CLI generator
- Avoids restarting entire workflow
- Maximum 2 retries to prevent infinite loops

### 3. Agent Specialization
- Each agent has a single, focused responsibility
- Separate agents can use different model parameters
- Easy to test and maintain independently

### 4. Stateful Conversation
- Maintains conversation history across turns
- Query rewriter resolves follow-up questions
- Context preserved for natural interaction

### 5. Multilingual Support
- Native support for English and Vietnamese
- Language parameter explicit (not auto-detected)
- Templates and responses localized

## Deployment

- Runs alongside K8s workflow in same codebase
- Shared infrastructure (LangGraph, Anthropic API)
- Separate vector database for vEPC documentation
- Environment-based configuration
- Docker containerized (via docker-compose)

## Performance Considerations

- Knowledge retrieval skipped for general intents
- Risk assessment skipped for read-only operations
- Validation retry limit prevents excessive API calls
- Vector DB caching for repeated queries
- Streaming enabled for real-time responses
