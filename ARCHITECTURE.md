# Architecture Deep Dive

Technical details for those implementing similar systems or extending this one.

## System Design

### Core Components

```
┌─────────────────────────────────────────────────┐
│              Agentic RAG System                 │
│                                                 │
│  User Query → LangGraph → Answer + Context     │
│                  ↓                              │
│          ┌───────┼───────┐                     │
│          ▼       ▼       ▼                     │
│      Weaviate  SpiceDB  OpenAI                 │
│      (Search)  (Auth)   (LLM)                  │
└─────────────────────────────────────────────────┘
```

### LangGraph State Machine

```
START
  ↓
Planning Node (Agent)
  ↓
Retrieval Node (Weaviate)
  ↓
Authorization Node (SpiceDB) ◄── Security Boundary (deterministic)
  ↓
Conditional:
├─ Has authorized docs? → Generation Node → END
└─ No authorized docs? → Reasoning Node → Conditional:
                                          ├─ Attempts left? → Planning Node (retry)
                                          └─ Max attempts? → Generation Node → END
```

### State Schema

```python
AgenticRAGState = TypedDict("AgenticRAGState", {
    # Input
    "query": str,
    "subject_id": str,
    "max_attempts": int,

    # Tracking
    "messages": List[BaseMessage],
    "reasoning": List[str],
    "retrieval_attempt": int,

    # Documents
    "retrieved_documents": List[Document],
    "authorized_documents": List[Document],
    "denied_count": int,

    # Results
    "authorization_passed": bool,
    "answer": str,
})
```

## Node Responsibilities

### Planning Node (Agentic)

**Purpose**: Agent plans retrieval strategy using available tools.

**Tools available:**
- `search_documents`: Query Weaviate
- `check_permission`: Verify permissions with SpiceDB

**Output**: Updates `messages`, `reasoning`, `retrieval_attempt`

**Example reasoning:**
```
"I'll search for documents about 'architecture' and 'engineering'.
I should retrieve 5 documents to ensure good coverage."
```

### Retrieval Node (Deterministic)

**Purpose**: Execute semantic/keyword search in Weaviate.

**Input**: `query` from state

**Operation**:
- Weaviate BM25/hybrid search
- Returns top-k documents (typically 5)
- No authorization filtering at this stage

**Output**: Updates `retrieved_documents`

### Authorization Node (Deterministic - Security Boundary)

**Purpose**: Filter documents by permissions using SpiceDB.

**Critical property**: This node ALWAYS runs and cannot be bypassed by the agent.

**Operation**:
```python
authorized = []
denied_count = 0

for doc in retrieved_documents:
    response = spicedb_client.CheckPermission(
        resource=f"document:{doc.id}",
        permission="view",
        subject=f"user:{subject_id}"
    )

    if response.permissionship == HAS_PERMISSION:
        authorized.append(doc)
    else:
        denied_count += 1

return {
    "authorized_documents": authorized,
    "denied_count": denied_count,
    "authorization_passed": len(authorized) > 0
}
```

**Output**: Updates `authorized_documents`, `denied_count`, `authorization_passed`

### Reasoning Node (Agentic)

**Purpose**: Agent analyzes authorization results and decides whether to retry.

**Input**: `authorized_documents`, `denied_count`, `retrieval_attempt`, `max_attempts`

**Decision logic:**
- If documents were denied and attempts remain: plan new strategy
- If max attempts reached: prepare explanation

**Output**: Updates `reasoning`, may update `retrieval_attempt`

### Generation Node (Agentic)

**Purpose**: Generate final answer incorporating authorization context.

**Input**: `query`, `authorized_documents`, `denied_count`, `reasoning`

**Behavior:**
- Uses authorized documents as context
- Mentions if documents were denied
- Explains access limitations transparently
- Provides helpful answer within constraints

**Output**: Updates `answer`

## Authorization Model (SpiceDB)

### Schema Definition

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

### Permission Check Flow

```
1. User makes query
   subject_id: "alice"

2. Weaviate retrieves documents
   [eng-001, eng-002, hr-001]

3. For each document, SpiceDB checks:

   eng-001:
   └─ viewer = engineering#member
      └─ alice is engineering#member?
         └─ alice → engineering → member ✅
         Result: ALLOWED

   hr-001:
   └─ viewer = hr_manager
      └─ alice is hr_manager?
         └─ alice ≠ hr_manager ❌
         Result: DENIED
```

### Relationship Graph Example

```
alice (user) ──member──> engineering (department)

eng-001 (document) ──viewer──> engineering#member
                               (allows all engineering members)

hr-001 (document) ──viewer──> hr_manager (user)
                              (allows only hr_manager)
```

## Security Architecture

### Trust Boundaries

```
┌───────────────────────────┐
│    Untrusted Zone         │
│  User Input, Query        │
└──────────┬────────────────┘
           ▼
┌───────────────────────────┐
│   Semi-Trusted Zone       │
│  Agent (LLM) + Tools      │
│  - Can plan strategies    │
│  - Can check permissions  │
│  - Cannot bypass auth     │
└──────────┬────────────────┘
           ▼
┌───────────────────────────┐
│   SECURITY BOUNDARY       │
│  Authorization Node       │
│  - Deterministic          │
│  - Always runs            │
│  - No LLM involvement     │
└──────────┬────────────────┘
           ▼
┌───────────────────────────┐
│    Trusted Zone           │
│  SpiceDB + Weaviate       │
│  Authorized data          │
└───────────────────────────┘
```

### Security Guarantees

1. **Authorization cannot be bypassed**
   ```python
   # Hardcoded in graph.py
   workflow.add_edge("retrieve", "authorize")
   # Agent cannot skip this edge
   ```

2. **Deterministic permission checks**
   ```python
   # Not LLM-based, uses SpiceDB directly
   response = spicedb_client.CheckPermission(...)
   if response.permissionship == HAS_PERMISSION:
       allow()
   ```

3. **Agent observes, doesn't control**
   ```python
   # Authorization happens first
   authorize() → reason()
   # Agent sees results, but doesn't make decisions
   ```

4. **Fail closed by default**
   ```python
   # Explicit permission required
   if not explicitly_allowed:
       deny()
   ```

## Conditional Logic

### After Authorization: Generate or Reason?

```python
def should_reason_or_generate(state: AgenticRAGState) -> str:
    if state["authorization_passed"]:
        return "generate"  # Have docs, answer the query
    else:
        return "reason"    # No docs, agent decides what to do
```

### After Reasoning: Retry or Generate?

```python
def should_retry_or_generate(state: AgenticRAGState) -> str:
    if (state["retrieval_attempt"] < state["max_attempts"]
        and len(state["authorized_documents"]) == 0):
        return "plan"      # Try again with different strategy
    else:
        return "generate"  # Give best answer we can
```

## Design Decisions

### Why Post-Filter Authorization?

**Alternative 1: Pre-filter (embed permissions in metadata)**
```python
# Query with permission filter
query.where({"department": user_department})
```
Problems:
- Limits search space (worse semantic results)
- Stale permissions (metadata not always current)
- Doesn't work with computed permissions

**Alternative 2: Post-filter (this approach)**
```python
# 1. Search without constraints (best semantic results)
docs = search(query)

# 2. Filter by up-to-date permissions
authorized = [d for d in docs if check_permission(d)]
```
Benefits:
- Best semantic search results
- Always current permissions
- Works with complex authorization logic

### Why LangGraph State Machine?

**Alternative: Pure ReAct loop**
```python
while not done:
    action = agent.choose_action()
    result = execute(action)
```
Problems:
- Agent controls flow (can skip steps)
- Harder to enforce security boundary
- Less observable

**LangGraph approach:**
```python
# Explicit state machine
workflow.add_edge("retrieve", "authorize")  # Always runs
```
Benefits:
- Enforces authorization node
- Observable state transitions
- Easier to debug/audit

### Why Deterministic Authorization Node?

**Not this:**
```python
def authorize(state):
    # Ask LLM to decide
    decision = llm("Should user access this doc?")
    return decision  # ❌ Non-deterministic
```

**This:**
```python
def authorize(state):
    # Direct SpiceDB check
    response = spicedb.CheckPermission(...)
    return response.permissionship == HAS_PERMISSION  # ✅ Deterministic
```

**Reason:** Security decisions must be deterministic, auditable, and policy-based.

## Agentic vs Pipeline RAG

### Pipeline RAG

```
Query
  ↓
Retrieve (fixed strategy)
  ↓
Authorize (filter)
  ↓
Generate (fixed prompt)
  ↓
Answer
```

**Characteristics:**
- Simple, predictable
- Fast (no agent reasoning overhead)
- Cannot adapt to failures
- Basic explanations

### Agentic RAG (This Implementation)

```
Query
  ↓
[Agent Plans] ← Can choose strategy
  ↓
Retrieve
  ↓
[Authorize] ← Security boundary
  ↓
[Agent Reasons] ← Can adapt
  ↓
Generate
  ↓
Answer + Transparent Explanation
```

**Characteristics:**
- Adaptive to failures
- Transparent reasoning
- Can retry with new strategies
- Rich explanations
- Slower (~2-3s overhead)

## Extension Points

### Adding New Nodes

```python
def custom_node(state: AgenticRAGState) -> dict:
    # Custom logic
    result = process(state["query"])
    return {"custom_field": result}

# Add to graph
workflow.add_node("custom", custom_node)
workflow.add_edge("authorize", "custom")
workflow.add_edge("custom", "reason")
```

### Adding New Tools

```python
from langchain.tools import BaseTool

class CustomTool(BaseTool):
    name = "custom_tool"
    description = "What this tool does"

    def _run(self, query: str) -> str:
        # Implementation
        return result

# Agent will have access in planning node
```

### Modifying Authorization Logic

```python
def authorization_node(state: AgenticRAGState):
    # Add custom checks
    if special_case(state["subject_id"]):
        return special_authorization(state)

    # Default SpiceDB logic
    return spicedb_authorization(state)
```

## Performance Characteristics

### Current Implementation

```
Query → Planning → Retrieval → Authorization → Reasoning → Generation
        ~2-3s      ~100-200ms   ~50ms/doc      ~2-3s       ~2-3s
```

**Total**: ~6-10 seconds per query

### Optimization Opportunities

1. **Batch permission checks**
   ```python
   # Instead of N individual checks
   results = spicedb.BulkCheckPermission(documents)
   ```

2. **Cache permission results**
   ```python
   @lru_cache(maxsize=1000)
   def check_permission(subject, resource):
       return spicedb.CheckPermission(...)
   ```

3. **Parallel agent calls**
   ```python
   # Run planning and permission checks in parallel
   await asyncio.gather(
       agent.plan(),
       check_permissions()
   )
   ```

## Observability

### State Tracking

Every node updates the state with:
- `messages`: What happened (for debugging)
- `reasoning`: Why it happened (agent's thought process)
- Metrics: counts, attempts, etc.

### Example Message Flow

```
[AIMessage] Planning: Searching for engineering documents...
[SystemMessage] Retrieved 3 documents from Weaviate
[SystemMessage] Authorization: 2/3 documents authorized (1 denied)
[AIMessage] Reasoning: User has partial access, generating answer from available docs
[AIMessage] Answer: Based on the 2 authorized documents...
```

### Debugging

```python
# Print state at each step
for event in graph.stream(initial_state):
    print(f"Node: {event}")
    print(f"State: {state}")
```

## Summary

This architecture demonstrates:

1. **Security**: Deterministic authorization that cannot be bypassed
2. **Flexibility**: Agent adapts strategies when authorization fails
3. **Transparency**: Clear reasoning about what was allowed/denied
4. **Observability**: Full state tracking through the flow
5. **Extensibility**: Easy to add nodes, tools, or custom logic

The key insight: **Agentic behavior and security guarantees are compatible**. The agent provides flexibility and explanation AFTER the security boundary, not as a replacement for it.
