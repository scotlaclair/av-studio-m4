# Repository Setup Instructions

## Automated Setup (This PR)
✅ Added `.github/copilot-instructions.md` for AI agents
✅ Added workflow configuration helper
✅ Added setup script for creating dev branch
✅ Updated README.md with AI Agent Development Workflow

## Manual Setup Required (Repository Owner: @scotlaclair)

### Step 0: Create dev Branch
After merging this PR to main, create the dev branch:

**Option A: Using the provided script**
```bash
cd av-studio-m4
./create-dev-branch.sh
```

**Option B: Manual creation**
```bash
git checkout main
git pull origin main
git checkout -b dev 896b57e2d205111df4ca61ee65562f8b689359f9
git push -u origin dev
```

### Step 1: Change Default Branch to dev
1. Go to: https://github.com/scotlaclair/av-studio-m4/settings
2. Scroll to "Default branch" section
3. Click the switch icon (⇄) next to `main`
4. Select `dev` from the dropdown
5. Click "Update" and confirm

### Step 2: Configure GitHub Actions Permissions
1. Go to: https://github.com/scotlaclair/av-studio-m4/settings/actions
2. Under "Workflow permissions":
   - Select ✅ "Read and write permissions"
   - Check ✅ "Allow GitHub Actions to create and approve pull requests"
3. Click "Save"

### Step 3: Protect main Branch
1. Go to: https://github.com/scotlaclair/av-studio-m4/settings/branches
2. Click "Add rule" or "Add classic branch protection rule"
3. Branch name pattern: `main`
4. Enable:
   - ✅ "Require a pull request before merging"
   - ✅ "Require approvals" (set to 1)
   - ✅ "Require branches to be up to date before merging"
5. Under "Restrict pushes":
   - Add `dev` as allowed branch to create PRs
6. Click "Create" or "Save changes"

### Step 4: Configure dev Branch (Optional - for extra protection)
1. Go to: https://github.com/scotlaclair/av-studio-m4/settings/branches
2. Click "Add rule"
3. Branch name pattern: `dev`
4. Enable:
   - ✅ "Allow force pushes" → Specify who: Add `github-actions[bot]`
5. This allows AI agents to work freely on dev

### Step 5: Verify Configuration
1. Check default branch shows as `dev` in repository home
2. Try creating a new PR - it should default to `dev` as base
3. Verify Actions can run and commit to `dev`

## After Setup
- Delete this `SETUP_INSTRUCTIONS.md` file
- All AI agents will automatically use `dev` as target
- `main` will be protected and require PR reviews
