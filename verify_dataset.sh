#!/bin/bash

# Verification script for the realistic document dataset implementation

set -e

echo "============================================================"
echo "Verifying Realistic Document Dataset Implementation"
echo "============================================================"

echo ""
echo "Step 1: Verify document generation"
echo "------------------------------------------------------------"
doc_count=$(ls -1 data/documents/*.txt 2>/dev/null | wc -l | xargs)
echo "✅ Found $doc_count documents (expected 50)"

if [ "$doc_count" -ne 50 ]; then
    echo "❌ Error: Expected 50 documents, found $doc_count"
    exit 1
fi

echo ""
echo "Step 2: Verify document distribution"
echo "------------------------------------------------------------"
eng_count=$(ls -1 data/documents/engineering-*.txt 2>/dev/null | wc -l | xargs)
sales_count=$(ls -1 data/documents/sales-*.txt 2>/dev/null | wc -l | xargs)
hr_count=$(ls -1 data/documents/hr-*.txt 2>/dev/null | wc -l | xargs)
finance_count=$(ls -1 data/documents/finance-*.txt 2>/dev/null | wc -l | xargs)
public_count=$(ls -1 data/documents/public-*.txt 2>/dev/null | wc -l | xargs)

echo "Engineering: $eng_count (expected 15)"
echo "Sales: $sales_count (expected 10)"
echo "HR: $hr_count (expected 10)"
echo "Finance: $finance_count (expected 10)"
echo "Public: $public_count (expected 5)"

if [ "$eng_count" -eq 15 ] && [ "$sales_count" -eq 10 ] && [ "$hr_count" -eq 10 ] && [ "$finance_count" -eq 10 ] && [ "$public_count" -eq 5 ]; then
    echo "✅ Document distribution correct"
else
    echo "❌ Error: Document distribution incorrect"
    exit 1
fi

echo ""
echo "Step 3: Verify document parser"
echo "------------------------------------------------------------"
python3 -c "
import sys
sys.path.insert(0, 'scripts')
from parse_documents import load_all_documents
docs = load_all_documents()
print(f'✅ Successfully parsed {len(docs)} documents')
assert len(docs) == 50, f'Expected 50 docs, got {len(docs)}'
assert all('doc_id' in doc for doc in docs), 'Missing doc_id'
assert all('title' in doc for doc in docs), 'Missing title'
assert all('content' in doc for doc in docs), 'Missing content'
assert all('department' in doc for doc in docs), 'Missing department'
print('✅ All documents have required fields')
"

echo ""
echo "Step 4: Verify scripts exist"
echo "------------------------------------------------------------"
scripts=(
    "scripts/document_templates.py"
    "scripts/generate_documents.py"
    "scripts/parse_documents.py"
    "scripts/verify_permissions.py"
)

for script in "${scripts[@]}"; do
    if [ -f "$script" ]; then
        echo "✅ $script exists"
    else
        echo "❌ Error: $script not found"
        exit 1
    fi
done

echo ""
echo "Step 5: Verify documentation"
echo "------------------------------------------------------------"
if [ -f "data/PERMISSIONS.md" ]; then
    echo "✅ data/PERMISSIONS.md exists"
else
    echo "❌ Error: data/PERMISSIONS.md not found"
    exit 1
fi

echo ""
echo "Step 6: Check permission verification script"
echo "------------------------------------------------------------"
echo "Note: Requires SpiceDB to be running. Skip if not available."
echo "To run permission tests manually:"
echo "  python3 scripts/verify_permissions.py"

echo ""
echo "============================================================"
echo "✅ All verification checks passed!"
echo "============================================================"
echo ""
echo "Summary:"
echo "  - 50 documents generated across 5 departments"
echo "  - Document templates and variations implemented"
echo "  - Document parser working correctly"
echo "  - All scripts and documentation in place"
echo ""
echo "Next steps:"
echo "  1. Ensure SpiceDB and Weaviate are running"
echo "  2. Run: python3 examples/setup_environment.py"
echo "  3. Run: python3 scripts/verify_permissions.py"
echo "  4. Run: python3 examples/basic_example.py"
echo ""
