# Agentic RAG with Fine-Grained Authorization

Build RAG systems where an agent adapts to authorization constraints instead of failing silently.

## The Problem

Traditional RAG retrieves documents by semantic similarity without considering permissions. This creates two issues:

1. **Security risk**: Users might see documents they shouldn't access
2. **Poor UX**: Silent failures when documents are denied, with no explanation

## The Solution

This implementation shows how to combine:
- **Agentic behavior**: Agent plans retrieval, reasons about failures, and explains constraints
- **Deterministic security**: SpiceDB authorization that cannot be bypassed
- **Transparency**: Users understand what they can/can't access and why

```
Traditional RAG:  Query → Retrieve → Generate
                           ↓
                    (no permission checks)

This approach:    Query → [Agent Plans] → Retrieve → [SpiceDB Authorizes] → [Agent Reasons] → Generate
                           ↓                          ↓                        ↓
                      Can adapt              Security boundary         Explains constraints
```

## Quick Example

```bash
# Alice (engineering department) queries engineering docs
Query: "What are our system architecture best practices?"
User: alice

Result:
✅ Retrieved: 3 documents
✅ Authorized: 2 documents (eng-001, eng-002)
❌ Denied: 1 document (hr-001)

Answer: "Based on the engineering documents, our system uses microservices
architecture with event-driven patterns..."
```

```bash
# Bob (sales department) queries engineering docs
Query: "What are our system architecture best practices?"
User: bob

Result:
✅ Retrieved: 3 documents
❌ Authorized: 0 documents
❌ Denied: 3 documents

Answer: "I don't have access to the engineering documents needed to answer
this question. This information is restricted to the engineering department."
```

The agent transparently explains access limitations instead of failing silently.

## Setup (5 minutes)

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- OpenAI API key

### Steps

```bash
# 1. Start services
docker-compose up -d

# 2. Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Configure
echo "OPENAI_API_KEY=sk-your-key-here" > .env

# 4. Initialize data
python3 examples/setup_environment.py

# 5. Run demo
python3 examples/basic_example.py
```

Expected output: 4 scenarios showing authorized access, denied access, and transparent explanations.

## How It Works

### 1. Authorization Model (SpiceDB)

```zed
definition user {}

definition department {
    relation member: user
}

definition document {
    relation viewer: user | department#member
    permission view = viewer
}
```

**Relationships:**
- `alice` is a member of `engineering` department
- `eng-001` document has viewer = `engineering#member`
- Result: alice can view eng-001 ✅

### 2. State Flow

```
User Query
    ↓
Planning Node ← Agent plans retrieval using tools
    ↓
Retrieval Node ← Weaviate semantic/keyword search
    ↓
Authorization Node ← SpiceDB filters (SECURITY BOUNDARY - cannot be bypassed)
    ↓
Conditional Branch:
├─ Has authorized docs → Generation Node
└─ No authorized docs → Reasoning Node → (retry or explain)
```

### 3. Security Guarantees

- **Authorization always runs**: Hardcoded in LangGraph workflow, agent cannot skip
- **Deterministic checks**: SpiceDB enforces permissions (no LLM involved)
- **Fail closed**: Access denied unless explicitly granted
- **Observable**: Full audit trail in state

### 4. Agentic Advantages

The agent can:
- **Plan**: Choose retrieval strategies based on query
- **Adapt**: Retry with different approaches when documents are denied
- **Explain**: Tell users why access was limited and what information is available
- **Check proactively**: Verify permissions before retrieval to save time

## When to Use This Pattern

**Use agentic RAG when:**
- Authorization failures need adaptive responses
- Users need clear explanations of access limitations
- Retrieval strategies should adapt to the query
- Transparency matters for trust/compliance

**Use pipeline RAG when:**
- Predictable, consistent flow is more important than flexibility
- Speed is critical (agentic adds ~2-3s for reasoning)
- Authorization is simple (all-or-nothing access)

## Project Structure

```
agentic-rag-weaviate/
├── agentic_rag/
│   ├── graph.py               # LangGraph state machine
│   ├── state.py               # State schema
│   ├── nodes/
│   │   ├── planning_node.py   # Agent plans retrieval
│   │   ├── retrieval_node.py  # Weaviate search
│   │   ├── authorization_node.py  # SpiceDB filtering (security boundary)
│   │   ├── reasoning_node.py  # Agent reasons about failures
│   │   └── generation_node.py # Final answer with context
│   └── tools/
│       ├── weaviate_tool.py   # Search tool
│       └── permission_tool.py # Permission check tool
├── examples/
│   ├── setup_environment.py   # Initialize data
│   └── basic_example.py       # End-to-end demo
├── data/
│   ├── schema.zed             # SpiceDB permission schema
│   └── sample_docs.json       # Sample documents
└── docker-compose.yml         # Weaviate + SpiceDB
```

## Configuration

Environment variables (`.env`):

```bash
# Required
OPENAI_API_KEY=sk-...

# Optional (defaults shown)
WEAVIATE_URL=http://localhost:8080
SPICEDB_ENDPOINT=localhost:50051
SPICEDB_TOKEN=devtoken
MAX_RETRIEVAL_ATTEMPTS=3
```

## Sample Scenarios

### Scenario 1: Authorized Access
- **User**: alice (engineering)
- **Query**: "system architecture best practices"
- **Result**: 2 engineering docs authorized, answer generated

### Scenario 2: Denied Access
- **User**: bob (sales)
- **Query**: "engineering system architecture"
- **Result**: 0 docs authorized, agent explains limitation

### Scenario 3: Partial Access
- **User**: alice (engineering)
- **Query**: "company policies"
- **Result**: Engineering docs authorized, HR docs denied, transparent explanation

## Key Design Decisions

**Why post-filter authorization?**
- Better semantic search (not limited by metadata filters)
- Always up-to-date permissions (computed by SpiceDB)
- Works with complex relationship-based policies

**Why LangGraph over ReAct?**
- Enforces security boundary (authorization node always runs)
- Observable state for debugging/auditing
- Clearer separation of concerns

**Why deterministic authorization node?**
- Security decisions must not be LLM-based
- Guarantees compliance with permission policies
- Agent reasons about results, not controls them

## Production Considerations

For production use, add:
- **Caching**: Cache SpiceDB permission checks
- **Observability**: LangSmith tracing, structured logging
- **Security**: TLS for SpiceDB, authentication layer
- **Performance**: Batch permission checks, async Weaviate client
- **Testing**: Integration tests with testcontainers

## Extending the System

**Add new permission rules:**
Edit `data/schema.zed` and reload with `examples/setup_environment.py`

**Add new documents:**
Edit `data/sample_docs.json` and re-run setup

**Customize agent behavior:**
Modify nodes in `agentic_rag/nodes/` or add new tools

**Change retrieval strategy:**
Update `retrieval_node.py` to use hybrid search, different ranking, etc.

## Testing

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_basic_flow.py::test_authorized_access
```

## Learn More

- **SpiceDB**: https://authzed.com/docs
- **Weaviate**: https://weaviate.io/developers/weaviate
- **LangGraph**: https://langchain-ai.github.io/langgraph/

## License

MIT
