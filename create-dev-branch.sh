#!/bin/bash
# Script to create the dev branch from main
# This should be run by the repository owner after merging the PR

set -e

echo "Creating dev branch from main (commit 896b57e)..."

# Ensure we're on main
git checkout main
git pull origin main

# Create dev branch from the specific commit
git checkout -b dev 896b57e2d205111df4ca61ee65562f8b689359f9

# Push dev branch to remote
git push -u origin dev

echo "✅ dev branch created and pushed to remote"
echo ""
echo "Next steps:"
echo "1. Go to repository settings to change default branch to 'dev'"
echo "2. Follow remaining instructions in SETUP_INSTRUCTIONS.md"
