# Contributing Guide

## Development Setup

```bash
# Clone repository
git clone <repo-url>
cd k8s-ops-workflow

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your credentials
```

## Code Style

We use Black for formatting and Ruff for linting:

```bash
# Format code
make format

# Lint code
make lint
```

## Testing

```bash
# Run all tests
make test

# Run specific test file
pytest tests/test_agents.py -v

# Run with coverage
pytest --cov=agents --cov=workflows tests/
```

## Adding New Agents

1. Create agent file in `agents/` directory
2. Inherit from `BaseAgent`
3. Implement `execute()` method
4. Add to `agents/__init__.py`
5. Write tests in `tests/test_agents.py`

Example:

```python
from core.base_agent import BaseAgent
from typing import Dict, Any

class MyNewAgent(BaseAgent):
    def __init__(self):
        super().__init__("MyNewAgent")
    
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Agent logic here
            result = {"status": "success"}
            self._add_response(state, result)
        except Exception as e:
            self._add_error(state, f"Failed: {str(e)}")
        
        return state
```

## Pull Request Process

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Make changes and add tests
4. Run tests and linting
5. Commit changes (`git commit -m 'Add amazing feature'`)
6. Push to branch (`git push origin feature/amazing-feature`)
7. Open Pull Request

## Commit Message Convention

```
type(scope): subject

body

footer
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

Example:
```
feat(agents): add timeline builder agent

Implements chronological event merging and T0 identification
for improved RCA correlation.

Closes #123
```

## Project Structure Guidelines

- Keep agents focused and single-purpose
- Use type hints for all function signatures
- Add docstrings to all classes and methods
- Handle errors gracefully with try/except
- Log important events using `_add_response()`
- Add warnings for non-critical issues

## Questions?

Open an issue for discussion before starting major changes.
