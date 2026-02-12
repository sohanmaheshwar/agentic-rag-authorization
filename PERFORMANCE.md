# Performance Guide

This document provides guidance on optimizing and monitoring the performance of the agentic RAG system.

## Current Performance Characteristics

### Typical Query Latency

**End-to-end latency:** 5-8 seconds per query

Breakdown by node:
- **Planning**: 1-2s (GPT-4 call for retrieval strategy)
- **Retrieval**: 0.5-1s (Weaviate BM25 search)
- **Authorization**: 40-50ms (SpiceDB bulk permission check)
- **Reasoning**: 1-2s (GPT-4 call, only if documents denied)
- **Generation**: 2-3s (GPT-4 call for final answer)

### Bottlenecks

1. **LLM calls** (70-80% of total time)
   - Planning node: 1-2s
   - Reasoning node: 1-2s (conditional)
   - Generation node: 2-3s
   - Total: 4-7s for LLM operations

2. **Vector search** (10-15% of total time)
   - Weaviate BM25 search: 0.5-1s

3. **Authorization** (1-2% of total time)
   - SpiceDB bulk check: 40-50ms (optimized)

## Optimizations Implemented

### 1. Connection Pooling

**Impact:** -100ms per query

Maintains singleton clients for SpiceDB and Weaviate instead of creating new connections per request.

```python
# Before: New client per request
client = create_insecure_spicedb_client(endpoint, token)  # 50-100ms

# After: Reused singleton
client = get_spicedb_client(endpoint, token)  # 0ms
```

**Files:**
- `agentic_rag/grpc_helpers.py` (SpiceDB client)
- `agentic_rag/weaviate_client.py` (Weaviate client)

### 2. Batch Permission Checks

**Impact:** -150ms for 5 documents (~5-10x faster)

Uses SpiceDB's `CheckBulkPermissions` API to check multiple permissions in a single gRPC request.

```python
# Before: Sequential checks
for doc in documents:
    response = client.CheckPermission(request)  # 40ms × 5 = 200ms

# After: Bulk check
response = client.CheckBulkPermissions(bulk_request)  # 45ms total
```

**Files:**
- `agentic_rag/authorization_helpers.py`

### 3. Structured Logging

**Impact:** Negligible overhead (<1ms)

JSON logging adds minimal overhead while providing valuable performance insights:

```json
{
  "logger": "agentic_rag.nodes.authorization",
  "duration_ms": 45.2,
  "authorized": 2,
  "denied": 1
}
```

Extract metrics:
```bash
# Average authorization time
python examples/simple_demo.py 2>&1 | \
  jq -r 'select(.logger == "agentic_rag.nodes.authorization") | .duration_ms' | \
  awk '{sum+=$1; count++} END {print sum/count}'
```

## Performance Monitoring

### Using Structured Logs

Extract performance metrics from JSON logs:

```bash
# 1. Average time per node
python examples/simple_demo.py 2>&1 | \
  jq -r 'select(.duration_ms) | "\(.logger) \(.duration_ms)"' | \
  awk '{sum[$1]+=$2; count[$1]++} END {for(k in sum) print k, sum[k]/count[k]}'

# 2. Authorization denial rates
python examples/simple_demo.py 2>&1 | \
  jq -r 'select(.logger == "agentic_rag.nodes.authorization") | "\(.authorized) \(.denied)"'

# 3. Error rates
python examples/simple_demo.py 2>&1 | \
  jq -r 'select(.level == "ERROR") | "\(.logger) \(.error_type)"' | \
  sort | uniq -c
```

### Key Metrics to Track

1. **End-to-end latency**
   - Target: < 10s (95th percentile)
   - Measure: Time from query input to final answer

2. **Authorization time**
   - Target: < 100ms for 5 documents
   - Current: ~45ms with bulk checks
   - Extract from: `nodes.authorization` logs

3. **Retrieval time**
   - Target: < 1s
   - Current: 0.5-1s
   - Extract from: `nodes.retrieval` logs

4. **Denial rate**
   - Important for security monitoring
   - Extract from: `denied` count in authorization logs

5. **Error rate**
   - Target: < 1% (excluding expected denials)
   - Extract from: ERROR level logs

## Future Optimization Opportunities

### 1. Permission Caching

**Potential impact:** -40ms per cached check

Cache SpiceDB results with short TTL (30-60s):

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_check_permission(subject_id, doc_id):
    # Cache expires on function reload
    return batch_check_permissions(...)
```

**Trade-offs:**
- ✅ Faster repeated checks
- ✅ Reduced SpiceDB load
- ❌ Stale permissions during TTL window
- ❌ Cache invalidation complexity
- ❌ Not suitable for high-security scenarios

**Recommendation:** Only implement if authorization is proven bottleneck (currently <2% of total time).

### 2. Async/Await Refactor

**Potential impact:** -2-3s through parallel LLM calls

Convert to async operations to parallelize LLM calls:

```python
# Current: Sequential LLM calls
plan = await llm.ainvoke(planning_prompt)      # 1-2s
answer = await llm.ainvoke(generation_prompt)  # 2-3s
# Total: 3-5s

# Future: Parallel where possible
# (depends on dependencies between calls)
```

**Trade-offs:**
- ✅ Better concurrency
- ✅ Lower latency for independent operations
- ❌ Large refactor (entire codebase)
- ❌ authzed library is sync-only (needs workaround)
- ❌ More complex error handling

**Recommendation:** Consider only if LLM latency becomes critical bottleneck.

### 3. Streaming Responses

**Potential impact:** Better perceived performance (no actual speedup)

Stream LLM generation for faster time-to-first-token:

```python
# Current: Wait for full response
answer = llm.invoke(prompt)  # Wait 2-3s

# Future: Stream tokens
async for token in llm.astream(prompt):
    yield token  # User sees progress immediately
```

**Trade-offs:**
- ✅ Better UX (perceived speed)
- ✅ Lower time-to-first-token
- ❌ More complex client handling
- ❌ Harder to implement with LangGraph state

### 4. Hybrid Search

**Potential impact:** Better relevance, similar speed

Combine BM25 (keyword) with vector search (semantic):

```python
# Current: BM25 only
results = weaviate_client.query.get(...).with_bm25(query)

# Future: Hybrid
results = weaviate_client.query.get(...).with_hybrid(
    query=query,
    alpha=0.5  # 50% BM25, 50% vector
)
```

**Trade-offs:**
- ✅ Better semantic relevance
- ✅ Robust to keyword variations
- ❌ Requires embedding model
- ❌ Slightly slower (~+100ms)

### 5. Proactive Permission Checks

**Potential impact:** Skip retrieval for queries with guaranteed denials

Check permissions before retrieval for document types:

```python
# Before retrieval, check if user has ANY access to document type
if not has_any_access(subject_id, "engineering"):
    return "You don't have access to engineering documents"
```

**Trade-offs:**
- ✅ Skip unnecessary retrieval
- ✅ Faster denials
- ❌ More complex logic
- ❌ Requires document type classification

## Scalability Considerations

### Current Limits

- **Throughput**: 1-2 queries/second per instance (limited by LLM latency)
- **Documents**: Tested with 10-50 documents, should scale to 1000s
- **Users**: No practical limit (SpiceDB scales horizontally)

### Scaling Strategies

1. **Horizontal scaling**: Multiple app instances behind load balancer
   - LLM calls are stateless (can run in parallel)
   - Connection pooling works per-instance

2. **LLM batching**: Queue multiple queries for batch processing
   - Trade latency for throughput
   - Useful for analytics workloads

3. **SpiceDB caching**: Enable SpiceDB's built-in caching layer
   - Configure in SpiceDB deployment
   - Reduces permission check latency

4. **Weaviate sharding**: Shard document collection by department/type
   - Reduces search space
   - Faster retrieval for large corpora

## Benchmarking

Run benchmarks to establish baseline:

```bash
# Install testing dependencies
pip install pytest-benchmark

# Run performance tests
pytest tests/test_performance.py --benchmark-only

# Example output:
# test_authorization_node     45.2ms (±2.1ms)
# test_retrieval_node         523ms (±45ms)
# test_end_to_end            6.8s (±0.3s)
```

Track performance over time:

```bash
# Save baseline
pytest tests/test_performance.py --benchmark-save=baseline

# Compare after changes
pytest tests/test_performance.py --benchmark-compare=baseline
```

## Troubleshooting Slow Queries

### 1. Enable DEBUG logging

```bash
LOG_LEVEL=DEBUG python examples/simple_demo.py 2>&1 | jq
```

Look for:
- High `duration_ms` values
- Multiple retries (reasoning node)
- Large document counts

### 2. Check external services

```bash
# Weaviate health
curl http://localhost:8080/v1/.well-known/ready

# SpiceDB health
grpcurl -plaintext localhost:50051 list

# Test SpiceDB latency
time grpcurl -plaintext -d '{"consistency": {"fully_consistent": true}}' \
  -H "authorization: Bearer devtoken" \
  localhost:50051 authzed.api.v1.PermissionsService/CheckPermission
```

### 3. Profile LLM calls

```bash
# Extract LLM call durations
python examples/simple_demo.py 2>&1 | \
  jq -r 'select(.logger | contains("nodes")) | "\(.logger) \(.duration_ms)"'
```

If LLM calls are slow (>5s):
- Check OpenAI API status
- Consider using gpt-3.5-turbo for faster (but lower quality) results
- Enable streaming responses

## Summary

**Current state:** Production-ready with key optimizations in place
- Connection pooling: ✅ Implemented
- Batch permissions: ✅ Implemented
- Structured logging: ✅ Implemented
- Error handling: ✅ Implemented

**Bottleneck:** LLM calls (70-80% of latency)
- Hard to optimize without quality trade-offs
- Consider streaming for better UX

**Authorization:** Highly optimized (1-2% of latency)
- Batch checks: 5-10x faster than sequential
- Connection pooling: Eliminates setup overhead
- Further optimization not recommended (diminishing returns)

**Recommended next steps:**
1. Monitor structured logs in production
2. Track key metrics (latency, denial rate, errors)
3. Only optimize further if specific bottlenecks identified
