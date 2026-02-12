#!/bin/bash

# Simple verification script for production improvements
# Checks code structure without requiring dependencies

echo "============================================================"
echo "PRODUCTION IMPROVEMENTS VERIFICATION"
echo "============================================================"
echo ""

PASS=0
FAIL=0

# Test 1: Check .env.example exists
echo "=== Test 1: Security - .env.example ===  "
if [ -f ".env.example" ]; then
    if grep -q "OPENAI_API_KEY=your-api-key-here" .env.example; then
        echo "✅ .env.example created with placeholder API key"
        ((PASS++))
    else
        echo "❌ .env.example missing placeholder"
        ((FAIL++))
    fi
else
    echo "❌ .env.example not found"
    ((FAIL++))
fi
echo ""

# Test 2: Check logging_config.py exists
echo "=== Test 2: Structured Logging ===
"
if [ -f "agentic_rag/logging_config.py" ]; then
    if grep -q "StructuredFormatter" agentic_rag/logging_config.py && \
       grep -q "get_logger" agentic_rag/logging_config.py; then
        echo "✅ Structured logging module created"
        ((PASS++))
    else
        echo "❌ Logging module missing required functions"
        ((FAIL++))
    fi
else
    echo "❌ logging_config.py not found"
    ((FAIL++))
fi
echo ""

# Test 3: Check weaviate_client.py exists
echo "=== Test 3: Weaviate Connection Pooling ==="
if [ -f "agentic_rag/weaviate_client.py" ]; then
    if grep -q "get_weaviate_client" agentic_rag/weaviate_client.py && \
       grep -q "_weaviate_client" agentic_rag/weaviate_client.py; then
        echo "✅ Weaviate connection pooling implemented"
        ((PASS++))
    else
        echo "❌ Weaviate client missing singleton pattern"
        ((FAIL++))
    fi
else
    echo "❌ weaviate_client.py not found"
    ((FAIL++))
fi
echo ""

# Test 4: Check SpiceDB connection pooling
echo "=== Test 4: SpiceDB Connection Pooling ==="
if grep -q "get_spicedb_client" agentic_rag/grpc_helpers.py && \
   grep -q "_spicedb_client" agentic_rag/grpc_helpers.py; then
    echo "✅ SpiceDB connection pooling implemented"
    ((PASS++))
else
    echo "❌ SpiceDB connection pooling not found"
    ((FAIL++))
fi
echo ""

# Test 5: Check authorization_helpers.py exists
echo "=== Test 5: Batch Permission Checks ==="
if [ -f "agentic_rag/authorization_helpers.py" ]; then
    if grep -q "batch_check_permissions" agentic_rag/authorization_helpers.py && \
       grep -q "CheckBulkPermissions" agentic_rag/authorization_helpers.py; then
        echo "✅ Batch permission checking implemented"
        ((PASS++))
    else
        echo "❌ Batch permission function incomplete"
        ((FAIL++))
    fi
else
    echo "❌ authorization_helpers.py not found"
    ((FAIL++))
fi
echo ""

# Test 6: Check validation.py exists
echo "=== Test 6: Input Validation ==="
if [ -f "agentic_rag/validation.py" ]; then
    if grep -q "validate_query" agentic_rag/validation.py && \
       grep -q "validate_subject_id" agentic_rag/validation.py && \
       grep -q "ValidationError" agentic_rag/validation.py; then
        echo "✅ Input validation implemented"
        ((PASS++))
    else
        echo "❌ Validation functions incomplete"
        ((FAIL++))
    fi
else
    echo "❌ validation.py not found"
    ((FAIL++))
fi
echo ""

# Test 7: Check error handling in retrieval node
echo "=== Test 7: Error Handling ==="
if grep -q "except Exception as e:" agentic_rag/nodes/retrieval_node.py && \
   grep -q "logger.error" agentic_rag/nodes/retrieval_node.py; then
    echo "✅ Error handling added to retrieval node"
    ((PASS++))
else
    echo "❌ Error handling missing in retrieval node"
    ((FAIL++))
fi
echo ""

# Test 8: Check logging in all nodes
echo "=== Test 8: Logging in Nodes ==="
NODE_COUNT=0
for node in planning retrieval authorization reasoning generation; do
    if grep -q "from ..logging_config import get_logger" "agentic_rag/nodes/${node}_node.py" 2>/dev/null; then
        ((NODE_COUNT++))
    fi
done

if [ $NODE_COUNT -eq 5 ]; then
    echo "✅ Logging added to all 5 nodes"
    ((PASS++))
else
    echo "❌ Logging only in $NODE_COUNT/5 nodes"
    ((FAIL++))
fi
echo ""

# Test 9: Check config has log_level
echo "=== Test 9: Configuration ==="
if grep -q "log_level:" agentic_rag/config.py && \
   grep -q "LOG_LEVEL" agentic_rag/config.py; then
    echo "✅ log_level configuration added"
    ((PASS++))
else
    echo "❌ log_level configuration missing"
    ((FAIL++))
fi
echo ""

# Test 10: Check PERFORMANCE.md exists
echo "=== Test 10: Documentation ==="
DOC_COUNT=0
if [ -f "PERFORMANCE.md" ]; then
    ((DOC_COUNT++))
fi
if grep -q "Production Features" README.md; then
    ((DOC_COUNT++))
fi

if [ $DOC_COUNT -eq 2 ]; then
    echo "✅ Documentation updated (README + PERFORMANCE.md)"
    ((PASS++))
else
    echo "❌ Documentation incomplete ($DOC_COUNT/2 files)"
    ((FAIL++))
fi
echo ""

# Summary
TOTAL=$((PASS + FAIL))
echo "============================================================"
echo "SUMMARY"
echo "============================================================"
echo ""
echo "Passed: $PASS/$TOTAL"
echo ""

if [ $PASS -eq $TOTAL ]; then
    echo "✅ All production improvements implemented successfully!"
    exit 0
else
    echo "⚠️  $FAIL tests failed"
    exit 1
fi
