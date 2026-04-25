#!/bin/bash
# Test runner script for Unix/Linux/Mac

echo "Running unit tests..."
python -m pytest tests/ -v --tb=short

echo ""
echo "Test coverage summary:"
python -m pytest tests/ --co -q
