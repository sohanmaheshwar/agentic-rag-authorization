# Contributing Guide

This guide covers development setup, extending the system, and contributing improvements.

## Development Setup

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- OpenAI API key

### Initial Setup

```bash
# 1. Clone repository
git clone <repository-url>
cd agentic-rag-weaviate

# 2. Start services
docker-compose up -d

# 3. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Configure environment
cp .env.example .env
# Edit .env with your OpenAI API key

# 6. Initialize data
python3 examples/setup_environment.py
```

### Verify Setup

```bash
# Check document count
ls -l data/documents/ | wc -l  # Should show 50 files

# Verify permissions
python3 scripts/verify_permissions.py  # Should pass 18/18 tests

# Run integration tests
python3 test_dataset_integration.py
```

## Project Structure

```
agentic-rag-weaviate/
├── agentic_rag/              # Core library
│   ├── graph.py              # LangGraph state machine
│   ├── state.py              # State schema
│   ├── config.py             # Configuration
│   ├── nodes/                # Graph nodes
│   │   ├── planning_node.py
│   │   ├── retrieval_node.py
│   │   ├── authorization_node.py
│   │   ├── reasoning_node.py
│   │   └── generation_node.py
│   └── tools/                # Agent tools
│       ├── weaviate_tool.py
│       └── permission_tool.py
├── examples/                 # Runnable examples
│   ├── setup_environment.py  # Data initialization
│   └── basic_example.py      # Demo scenarios
├── scripts/                  # Utilities
│   ├── document_templates.py # Document templates
│   ├── generate_documents.py # Document generator
│   ├── parse_documents.py    # Document parser
│   └── verify_permissions.py # Permission tests
├── data/
│   ├── documents/            # 50 .txt documents
│   ├── schema.zed            # SpiceDB schema
│   ├── sample_docs.json      # Legacy sample
│   └── PERMISSIONS.md        # Permission matrix
└── tests/                    # Test suite
```

## Extending the System

### Adding Documents

**Option 1: Manual Creation**

Create a new .txt file in `data/documents/`:

```txt
# File: data/documents/engineering-guide-006.txt

Title: API Design Guidelines

Department: Engineering
Category: Guide

Content:
REST API design principles for microservices...
```

Naming convention: `{department}-{category}-{number}.txt`

**Option 2: Regenerate All Documents**

```bash
# Modify templates
vim scripts/document_templates.py

# Regenerate
python3 scripts/generate_documents.py

# Reload into Weaviate
python3 examples/setup_environment.py
```

### Adding Permissions

Edit `examples/setup_environment.py` and add relationships:

```python
# Department-based access
write_relationships(client, "document:new-doc-001#viewer@department:engineering#member")

# Individual user access
write_relationships(client, "document:new-doc-001#viewer@user:alice")

# Cross-department access
write_relationships(client, "document:shared-doc#viewer@department:sales#member")
write_relationships(client, "document:shared-doc#viewer@department:engineering#member")
```

Then reload:
```bash
python3 examples/setup_environment.py
```

### Adding Users

1. **Add user-department relationship:**

```python
# In examples/setup_environment.py
write_relationships(client, "department:engineering#member@user:new_user")
```

2. **Test the new user:**

```python
# In examples/basic_example.py
await run_query(graph, "What are our policies?", "new_user")
```

3. **Update documentation:**

Add to `data/PERMISSIONS.md`:
```markdown
| new_user | engineering | All 15 engineering documents |
```

### Customizing Agent Behavior

**Modify Planning Strategy:**

Edit `agentic_rag/nodes/planning_node.py`:

```python
def planning_node(state: AgenticRAGState):
    # Add custom planning logic
    if "urgent" in state["query"].lower():
        # Use different retrieval strategy for urgent queries
        return custom_urgent_planning(state)

    # Default planning
    return default_planning(state)
```

**Add New Tools:**

Create a new tool in `agentic_rag/tools/`:

```python
# agentic_rag/tools/custom_tool.py
from langchain.tools import BaseTool

class CustomTool(BaseTool):
    name = "custom_tool"
    description = "What this tool does and when to use it"

    def _run(self, query: str) -> str:
        # Implementation
        result = process(query)
        return result
```

Register in planning node:
```python
from agentic_rag.tools.custom_tool import CustomTool

tools = [weaviate_tool, permission_tool, CustomTool()]
```

**Add New Node:**

```python
# agentic_rag/nodes/custom_node.py
from agentic_rag.state import AgenticRAGState

def custom_node(state: AgenticRAGState) -> dict:
    # Custom processing
    result = process(state["query"])

    return {
        "custom_field": result,
        "messages": state["messages"] + [SystemMessage(content=f"Custom: {result}")]
    }
```

Register in `agentic_rag/graph.py`:
```python
workflow.add_node("custom", custom_node)
workflow.add_edge("authorize", "custom")
workflow.add_edge("custom", "reason")
```

### Changing Retrieval Strategy

**Switch to Hybrid Search:**

Edit `agentic_rag/nodes/retrieval_node.py`:

```python
# Change from BM25
response = (
    client.query
    .get(...)
    .with_bm25(query=query)  # Current
)

# To hybrid search
response = (
    client.query
    .get(...)
    .with_hybrid(
        query=query,
        alpha=0.5  # 50% keyword, 50% semantic
    )
)
```

Note: Hybrid search requires embedding model configuration.

**Adjust Result Count:**

```python
response = (
    client.query
    .get(...)
    .with_limit(10)  # Increase from 5 to 10
)
```

### Modifying Authorization Logic

**Add Custom Authorization Rules:**

Edit `agentic_rag/nodes/authorization_node.py`:

```python
def authorization_node(state: AgenticRAGState):
    # Custom rule: admins see everything
    if state["subject_id"] == "admin":
        return {
            "authorized_documents": state["retrieved_documents"],
            "authorization_passed": True,
            "denied_count": 0
        }

    # Standard SpiceDB check
    return spicedb_authorization(state)
```

**Modify SpiceDB Schema:**

Edit `data/schema.zed`:

```zed
definition user {}

definition department {
    relation member: user
    relation admin: user  // NEW
}

definition document {
    relation viewer: user | department#member
    relation owner: user  // NEW

    permission view = viewer + owner
    permission edit = owner  // NEW
}
```

Reload schema:
```bash
python3 examples/setup_environment.py
```

## Testing

### Run All Tests

```bash
# Unit tests
pytest tests/

# Integration tests
python3 test_dataset_integration.py

# Permission verification
python3 scripts/verify_permissions.py

# Dataset verification
./verify_dataset.sh
```

### Add New Tests

Create tests in `tests/` directory:

```python
# tests/test_custom_feature.py
import pytest
from agentic_rag.graph import build_agentic_rag_graph

@pytest.mark.asyncio
async def test_custom_feature():
    graph = build_agentic_rag_graph()
    result = await graph.ainvoke({
        "query": "test query",
        "subject_id": "alice",
        # ... initial state
    })

    assert result["answer"] is not None
    assert len(result["authorized_documents"]) > 0
```

Run with:
```bash
pytest tests/test_custom_feature.py -v
```

## Debugging

### Enable Debug Logging

```bash
export LOG_LEVEL=DEBUG
python3 examples/basic_example.py 2>&1 | jq
```

### Inspect State

```python
# Add to your script
for event in graph.stream(initial_state):
    print(f"Event: {event}")
    print(f"State keys: {event.keys()}")
```

### Test Individual Nodes

```python
from agentic_rag.nodes.retrieval_node import retrieval_node
from agentic_rag.state import AgenticRAGState

# Create test state
state = {
    "query": "test query",
    "subject_id": "alice",
    "messages": [],
    # ... other required fields
}

# Test node directly
result = retrieval_node(state)
print(f"Retrieved: {len(result['retrieved_documents'])} docs")
```

### Verify Services

```bash
# Weaviate health check
curl http://localhost:8080/v1/.well-known/ready

# SpiceDB connectivity
grpcurl -plaintext localhost:50051 list

# Test SpiceDB permission
grpcurl -plaintext \
  -H "authorization: Bearer devtoken" \
  -d '{"resource":{"object_type":"document","object_id":"eng-001"},"permission":"view","subject":{"object":{"object_type":"user","object_id":"alice"}}}' \
  localhost:50051 authzed.api.v1.PermissionsService/CheckPermission
```

## Performance Optimization

See [PERFORMANCE.md](PERFORMANCE.md) for:
- Profiling techniques
- Optimization strategies
- Caching patterns
- Async/await refactoring

## Documentation

When adding features, update:

1. **Code comments** - Document complex logic
2. **Docstrings** - All public functions
3. **README.md** - If changing core concepts
4. **ARCHITECTURE.md** - If adding nodes or changing flow
5. **PERMISSIONS.md** - If adding permission patterns

## Common Tasks

### Reset Everything

```bash
# Stop services
docker-compose down -v

# Clean Python cache
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# Restart
docker-compose up -d
python3 examples/setup_environment.py
```

### Update Dependencies

```bash
# Update requirements.txt
pip install --upgrade <package>
pip freeze > requirements.txt

# Test compatibility
pytest tests/
```

### Add New Department

```bash
# 1. Generate documents
python3 scripts/generate_documents.py  # Modify first to add new dept

# 2. Add relationships
vim examples/setup_environment.py  # Add dept relationships

# 3. Reload
python3 examples/setup_environment.py

# 4. Test
python3 scripts/verify_permissions.py
```

## Code Style

- Follow PEP 8
- Use type hints
- Add docstrings to public functions
- Keep functions focused (single responsibility)
- Prefer explicit over implicit

## Questions?

- Open an issue for bugs
- Start a discussion for feature ideas
- Check ARCHITECTURE.md for design decisions

## License

MIT
