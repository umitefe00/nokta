#!/bin/bash
# Test script for Nokta workflows
# This script creates test scenarios to validate CI/CD workflows

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Nokta Workflow Test Suite ===${NC}\n"

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}ERROR: GitHub CLI (gh) is not installed.${NC}"
    echo "Install: https://cli.github.com/"
    exit 1
fi

# Check if user is authenticated
if ! gh auth status &> /dev/null; then
    echo -e "${RED}ERROR: Not authenticated with GitHub CLI.${NC}"
    echo "Run: gh auth login"
    exit 1
fi

# Get repo info
REPO_OWNER=$(gh repo view --json owner -q .owner.login)
REPO_NAME=$(gh repo view --json name -q .name)
echo -e "${GREEN}Repository: $REPO_OWNER/$REPO_NAME${NC}\n"

# Function to create a test branch and PR
create_test_pr() {
    local branch_name=$1
    local pr_title=$2
    local pr_body=$3
    local base_branch=${4:-main}

    echo -e "${YELLOW}Creating branch: $branch_name${NC}"

    # Create and checkout branch
    git checkout -b "$branch_name" "$base_branch" 2>/dev/null || git checkout "$branch_name"

    # Let caller make changes
    echo -e "${BLUE}Branch created. Make your changes now, then press ENTER to continue...${NC}"
    read -r

    # Commit changes
    git add .
    git commit -m "test: $pr_title" || echo "No changes to commit"

    # Push branch
    git push -u origin "$branch_name"

    # Create PR
    echo -e "${YELLOW}Creating PR...${NC}"
    PR_URL=$(gh pr create \
        --base "$base_branch" \
        --head "$branch_name" \
        --title "$pr_title" \
        --body "$pr_body")

    echo -e "${GREEN}PR created: $PR_URL${NC}"
    echo "$PR_URL"
}

# Function to wait for CI and show status
wait_for_ci() {
    local pr_number=$1
    local timeout=${2:-300}  # 5 minutes default

    echo -e "${YELLOW}Waiting for CI to complete (timeout: ${timeout}s)...${NC}"

    local elapsed=0
    while [ $elapsed -lt $timeout ]; do
        # Get CI status
        local status=$(gh pr checks "$pr_number" --json state -q '.[0].state' 2>/dev/null || echo "PENDING")

        if [ "$status" == "SUCCESS" ]; then
            echo -e "${GREEN}✅ CI passed!${NC}"
            return 0
        elif [ "$status" == "FAILURE" ]; then
            echo -e "${RED}❌ CI failed!${NC}"
            gh pr checks "$pr_number"
            return 1
        else
            echo -ne "\rStatus: $status (${elapsed}s elapsed)   "
            sleep 5
            elapsed=$((elapsed + 5))
        fi
    done

    echo -e "\n${RED}Timeout waiting for CI${NC}"
    return 1
}

# Function to check if PR was merged
check_if_merged() {
    local pr_number=$1
    local state=$(gh pr view "$pr_number" --json state -q .state)

    if [ "$state" == "MERGED" ]; then
        echo -e "${GREEN}✅ PR was auto-merged!${NC}"
        return 0
    else
        echo -e "${YELLOW}⏸️  PR not merged (state: $state)${NC}"
        return 1
    fi
}

# Test scenarios
run_test_suite() {
    echo -e "${BLUE}=== Test Scenarios ===${NC}\n"

    # Scenario 1: Path A - Section Edit (Auto-merge)
    echo -e "${BLUE}--- Scenario 1: Path A (Section Edit) ---${NC}"
    echo "This tests editing a section in program.md"
    echo "Expected: Auto-merge if score ≥ baseline"
    echo ""
    read -p "Run this test? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Prepare test
        git checkout main
        git pull origin main

        # Create branch
        BRANCH_NAME="test/section-01-identity-$(date +%s)"
        PR_URL=$(create_test_pr "$BRANCH_NAME" \
            "test(section-01): add test improvement to identity section" \
            "## Test PR for Path A (Section Edit)

This PR tests the section edit workflow.

**Changes:**
- Minor improvement to section 1 (IDENTITY) in program.md

**Expected outcome:**
- CI scores the section
- If score ≥ baseline → Auto-merge ✅
- If score < baseline → Auto-reject ❌

**Test ID:** scenario-1-path-a" \
            "main")

        PR_NUMBER=$(echo "$PR_URL" | grep -oP '\d+$')

        # Wait for CI
        if wait_for_ci "$PR_NUMBER"; then
            sleep 10  # Give auto-merge time
            check_if_merged "$PR_NUMBER"
        fi

        # Cleanup
        echo -e "${YELLOW}Cleanup: Delete test branch? (y/n)${NC}"
        read -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git checkout main
            git branch -D "$BRANCH_NAME" 2>/dev/null || true
            git push origin --delete "$BRANCH_NAME" 2>/dev/null || true
        fi
    fi

    # Scenario 2: Path C - Implementation (Auto-merge path)
    echo -e "\n${BLUE}--- Scenario 2: Path C (Implementation - Auto-merge) ---${NC}"
    echo "This tests implementation PR with all gates passing"
    echo "Expected: Auto-merge if all criteria met"
    echo ""
    read -p "Run this test? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git checkout main
        git pull origin main

        BRANCH_NAME="test/implement-dummy-$(date +%s)"

        echo -e "${BLUE}Instructions:${NC}"
        echo "1. Create a simple TypeScript file with tests"
        echo "2. Ensure all hard gates pass (tsc, eslint, test, bundle)"
        echo "3. No new dependencies"
        echo "4. Press ENTER when ready"

        PR_URL=$(create_test_pr "$BRANCH_NAME" \
            "feat(test): add dummy implementation for workflow testing" \
            "## Test PR for Path C (Implementation - Auto-merge)

This PR tests the implementation workflow with auto-merge.

**Changes:**
- Simple TypeScript file with tests
- All hard gates should pass

**Expected outcome:**
- ✅ TypeScript: 20/20
- ✅ ESLint: 20/20
- ✅ Tests: 20/20
- ✅ Bundle: 20/20
- ✅ Verdict: PASS
- 🤖 Auto-merge to main

**Test ID:** scenario-2-path-c-auto

## Evidence
(Add screenshot here)

## Checklist
- [x] All hard gates pass locally
- [x] Tests validate user behavior
- [x] No new dependencies" \
            "main")

        PR_NUMBER=$(echo "$PR_URL" | grep -oP '\d+$')

        if wait_for_ci "$PR_NUMBER" 600; then  # 10 min timeout
            sleep 15  # Give auto-merge time
            check_if_merged "$PR_NUMBER"
        fi
    fi

    # Scenario 3: Path C - Implementation (Human review needed)
    echo -e "\n${BLUE}--- Scenario 3: Path C (Implementation - Human review) ---${NC}"
    echo "This tests implementation PR that needs human review"
    echo "Expected: CI marks as REVIEW, waits for maintainer"
    echo ""
    read -p "Run this test? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git checkout main
        git pull origin main

        BRANCH_NAME="test/implement-with-dep-$(date +%s)"

        echo -e "${BLUE}Instructions:${NC}"
        echo "1. Modify package.json to add a new dependency"
        echo "2. This will trigger human review"
        echo "3. Press ENTER when ready"

        PR_URL=$(create_test_pr "$BRANCH_NAME" \
            "feat(test): add feature with new dependency (needs review)" \
            "## Test PR for Path C (Implementation - Human review)

This PR tests the implementation workflow with human review required.

**Changes:**
- Code that adds a new npm dependency

**Expected outcome:**
- ✅ Hard gates pass
- ⏸️  Verdict: REVIEW (new dependency detected)
- 👤 Waits for maintainer approval
- Maintainer can assign subjective score (0-20pt)

**Test ID:** scenario-3-path-c-review

## Dependency justification
(Explain why this dependency is needed)

## Evidence
(Add screenshot here)" \
            "main")

        PR_NUMBER=$(echo "$PR_URL" | grep -oP '\d+$')

        if wait_for_ci "$PR_NUMBER" 600; then
            echo -e "${YELLOW}Checking verdict...${NC}"
            sleep 5

            # Check for review comment
            gh pr view "$PR_NUMBER"

            echo -e "\n${BLUE}To complete this test:${NC}"
            echo "1. Verify CI comment shows ⏸️ REVIEW verdict"
            echo "2. Maintainer adds comment: /score 15"
            echo "3. Maintainer manually merges PR"
            echo "4. Check leaderboard for score: 80 + 15 = 95pt"
        fi
    fi

    # Scenario 4: Path C - Implementation (Failure)
    echo -e "\n${BLUE}--- Scenario 4: Path C (Implementation - Failure) ---${NC}"
    echo "This tests implementation PR with TypeScript errors"
    echo "Expected: CI blocks with FAIL verdict"
    echo ""
    read -p "Run this test? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git checkout main
        git pull origin main

        BRANCH_NAME="test/implement-broken-$(date +%s)"

        echo -e "${BLUE}Instructions:${NC}"
        echo "1. Create TypeScript file with intentional type error"
        echo "2. This will fail TypeScript gate"
        echo "3. Press ENTER when ready"

        PR_URL=$(create_test_pr "$BRANCH_NAME" \
            "feat(test): add broken implementation (should fail)" \
            "## Test PR for Path C (Implementation - Failure)

This PR tests the implementation workflow with failing gates.

**Changes:**
- Code with intentional TypeScript errors

**Expected outcome:**
- ❌ TypeScript: FAIL
- ❌ Verdict: FAIL
- 🚫 PR blocked
- Clear error message in CI comment

**Test ID:** scenario-4-path-c-fail" \
            "main")

        PR_NUMBER=$(echo "$PR_URL" | grep -oP '\d+$')

        if ! wait_for_ci "$PR_NUMBER" 300; then
            echo -e "${GREEN}Expected failure occurred!${NC}"
            gh pr view "$PR_NUMBER"
        fi
    fi

    echo -e "\n${GREEN}=== Test suite complete ===${NC}"
}

# Main menu
show_menu() {
    echo "1) Run full test suite"
    echo "2) Test Scenario 1 (Path A - Section edit)"
    echo "3) Test Scenario 2 (Path C - Auto-merge)"
    echo "4) Test Scenario 3 (Path C - Human review)"
    echo "5) Test Scenario 4 (Path C - Failure)"
    echo "6) Exit"
    echo ""
    read -p "Select option: " option

    case $option in
        1) run_test_suite ;;
        2) echo "TODO: Individual scenario" ;;
        3) echo "TODO: Individual scenario" ;;
        4) echo "TODO: Individual scenario" ;;
        5) echo "TODO: Individual scenario" ;;
        6) exit 0 ;;
        *) echo "Invalid option" ;;
    esac
}

# Run
show_menu
