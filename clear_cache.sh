#!/bin/bash
# Clear Python and Streamlit cache files

echo "🧹 Clearing cache files..."

# Clear Python cache
echo "  - Clearing __pycache__ directories..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

echo "  - Clearing .pyc files..."
find . -name "*.pyc" -delete 2>/dev/null || true

# Clear Streamlit cache
echo "  - Clearing Streamlit cache..."
rm -rf ~/.streamlit 2>/dev/null || true
rm -rf .streamlit/cache 2>/dev/null || true

echo "✅ Cache cleared successfully!"
echo ""
echo "You can now run: streamlit run app.py"
