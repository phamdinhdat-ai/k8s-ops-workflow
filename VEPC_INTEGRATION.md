# Integrating vEPC Workflow into Your Application

This guide shows how to integrate the vEPC workflow into your existing application.

## Basic Integration

### 1. Import and Initialize

```python
from workflows.vepc import run_vepc_workflow
import asyncio

async def handle_user_query(query: str, language: str = "en"):
    """Handle a user query through the vEPC workflow."""
    result = await run_vepc_workflow(
        user_query=query,
        language=language
    )
    return result
```

### 2. With Conversation History

```python
class VEPCAssistant:
    def __init__(self):
        self.conversation_history = []
    
    async def process_query(self, query: str, language: str = "en"):
        """Process query with conversation context."""
        result = await run_vepc_workflow(
            user_query=query,
            language=language,
            conversation_history=self.conversation_history
        )
        
        # Update conversation history
        self.conversation_history.append({
            "user": query,
            "assistant": result["final_response"]
        })
        
        # Keep only last 3 turns
        if len(self.conversation_history) > 3:
            self.conversation_history = self.conversation_history[-3:]
        
        return result
```

## Web API Integration

### FastAPI Example

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from workflows.vepc import run_vepc_workflow
from typing import Optional, List
import uuid

app = FastAPI()

# In-memory session store (use Redis in production)
sessions = {}

class QueryRequest(BaseModel):
    query: str
    language: str = "en"
    session_id: Optional[str] = None

class QueryResponse(BaseModel):
    response: str
    intent: str
    cli_commands: List[str]
    risk_level: Optional[str]
    session_id: str

@app.post("/vepc/query", response_model=QueryResponse)
async def process_vepc_query(request: QueryRequest):
    """Process vEPC query via API."""
    
    # Get or create session
    session_id = request.session_id or str(uuid.uuid4())
    history = sessions.get(session_id, [])
    
    try:
        result = await run_vepc_workflow(
            user_query=request.query,
            language=request.language,
            conversation_history=history
        )
        
        # Update session history
        history.append({
            "user": request.query,
            "assistant": result["final_response"]
        })
        sessions[session_id] = history[-3:]
        
        return QueryResponse(
            response=result["final_response"],
            intent=result["intent"],
            cli_commands=result["cli_commands"],
            risk_level=result["risk_level"],
            session_id=session_id
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## CLI Integration

### Interactive CLI

```python
import asyncio
from workflows.vepc import run_vepc_workflow

async def interactive_cli():
    """Interactive CLI for vEPC workflow."""
    print("vEPC Assistant - Interactive Mode")
    print("Type 'exit' to quit, 'clear' to reset conversation")
    
    history = []
    language = "en"
    
    while True:
        try:
            query = input(f"[{language}] You: ").strip()
            
            if query.lower() == "exit":
                break
            
            if query.lower() == "clear":
                history = []
                print("Conversation cleared.")
                continue
            
            if not query:
                continue
            
            result = await run_vepc_workflow(
                user_query=query,
                language=language,
                conversation_history=history
            )
            
            print(f"Assistant: {result['final_response']}")
            
            if result['cli_commands']:
                print(f"CLI: {result['cli_commands']}")
            if result['risk_level']:
                print(f"Risk: {result['risk_level']}")
            
            # Update history
            history.append({
                "user": query,
                "assistant": result["final_response"]
            })
            history = history[-3:]
        
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(interactive_cli())
```

## Production Considerations

### Session Management
Use Redis for distributed session storage in production.

### Rate Limiting
Implement rate limiting to prevent abuse.

### Monitoring
Log query metrics, intent distribution, and error rates.

### Caching
Cache responses for identical queries to reduce API costs.
