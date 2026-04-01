# TESTING.md — Workflow Testing Guide

This document provides step-by-step instructions for testing Nokta CI/CD workflows.

---

## Prerequisites

1. **GitHub CLI installed:**
   ```bash
   # Check if installed
   gh --version

   # Install if needed (Ubuntu/Debian)
   curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
   echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
   sudo apt update
   sudo apt install gh
   ```

2. **Authenticate GitHub CLI:**
   ```bash
   gh auth login
   # Follow prompts to authenticate
   ```

3. **Repository setup:**
   ```bash
   cd /path/to/nokta
   git remote -v  # Verify origin is set
   ```

---

## Test Scenarios

### Scenario 1: Path A — Section Edit (Auto-merge)

**Objective:** Test program.md section editing workflow with auto-merge.

**Steps:**

1. **Create test branch:**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b test/section-01-improvement
   ```

2. **Make a small improvement to program.md:**
   ```bash
   # Example: Add a sentence to section 1 (IDENTITY)
   # Edit program.md, find section 1, add:
   # "This project demonstrates spec-driven development."
   ```

3. **Commit and push:**
   ```bash
   git add program.md
   git commit -m "test(section-01): add clarity to identity section"
   git push -u origin test/section-01-improvement
   ```

4. **Create PR via GitHub CLI:**
   ```bash
   gh pr create \
     --title "test(section-01): add clarity to identity section" \
     --body "Testing Path A workflow. Should auto-merge if score ≥ baseline." \
     --base main
   ```

5. **Watch CI:**
   ```bash
   # Get PR number
   gh pr list --head test/section-01-improvement

   # Watch CI status
   gh pr checks <PR_NUMBER> --watch
   ```

6. **Verify outcome:**
   - CI should score the section
   - If score ≥ baseline → PR auto-merges ✅
   - Check: `gh pr view <PR_NUMBER>`

7. **Cleanup:**
   ```bash
   git checkout main
   git branch -D test/section-01-improvement
   git push origin --delete test/section-01-improvement
   ```

---

### Scenario 2: Path B — New Spec File (Auto-merge)

**Objective:** Test creating a new feature spec with auto-merge.

**Steps:**

1. **Create test branch:**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b test/spec-dummy-feature
   ```

2. **Create a minimal spec file:**
   ```bash
   cp specs/TEMPLATE.md specs/test-dummy-feature.md
   ```

3. **Fill in the spec:**
   ```markdown
   # test-dummy-feature.md

   ## 1. IDENTITY

   **Name:** Test Dummy Feature
   **Purpose:** Testing spec creation workflow
   **Version:** v0.1.0

   ## 2. NON-GOALS

   - Will not implement actual feature
   - Will not add UI
   - Will not add backend
   - Will not add tests
   - Will not add dependencies

   ## 3. DATA CONTRACTS

   ```typescript
   interface DummyFeature {
     id: string;
     name: string;
     enabled: boolean;
   }
   ```

   ## 4. OBJECTIVE FUNCTION

   Metric: `test_dummy_feature_score = 100` (always passes)

   ## 5. RATCHET RULE

   First PR establishes baseline. Subsequent PRs must maintain score.
   ```

4. **Commit and push:**
   ```bash
   git add specs/test-dummy-feature.md
   git commit -m "spec(test-dummy): add dummy feature spec for testing"
   git push -u origin test/spec-dummy-feature
   ```

5. **Create PR:**
   ```bash
   gh pr create \
     --title "spec(test-dummy): add dummy feature spec" \
     --body "Testing Path B workflow. First PR should auto-merge if score > 0." \
     --base main
   ```

6. **Watch CI and verify auto-merge:**
   ```bash
   gh pr checks <PR_NUMBER> --watch
   gh pr view <PR_NUMBER>
   ```

---

### Scenario 3: Path C — Implementation (Auto-merge)

**Objective:** Test implementation PR with all gates passing → auto-merge.

**Steps:**

1. **Create test branch:**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b test/implement-dummy-util
   ```

2. **Create a simple TypeScript file:**
   ```bash
   mkdir -p src/utils
   cat > src/utils/dummy.ts <<'EOF'
   /**
    * Dummy utility for testing workflow
    */
   export function addNumbers(a: number, b: number): number {
     return a + b;
   }

   export function multiplyNumbers(a: number, b: number): number {
     return a * b;
   }
   EOF
   ```

3. **Create a test file:**
   ```bash
   mkdir -p src/utils/__tests__
   cat > src/utils/__tests__/dummy.test.ts <<'EOF'
   import { addNumbers, multiplyNumbers } from '../dummy';

   describe('dummy utils', () => {
     it('should add numbers correctly', () => {
       expect(addNumbers(2, 3)).toBe(5);
       expect(addNumbers(-1, 1)).toBe(0);
     });

     it('should multiply numbers correctly', () => {
       expect(multiplyNumbers(2, 3)).toBe(6);
       expect(multiplyNumbers(-2, 3)).toBe(-6);
     });
   });
   EOF
   ```

4. **Verify locally (IMPORTANT):**
   ```bash
   npx tsc --noEmit      # Should pass
   npx eslint . --ext .ts,.tsx  # Should pass
   npm test              # Should pass
   ```

5. **Commit and push:**
   ```bash
   git add src/
   git commit -m "feat(utils): add dummy utility functions for testing"
   git push -u origin test/implement-dummy-util
   ```

6. **Create PR:**
   ```bash
   gh pr create \
     --title "feat(utils): add dummy utility functions" \
     --body "$(cat <<'BODY'
   ## Test PR for Path C (Implementation - Auto-merge)

   This PR tests the implementation workflow with auto-merge.

   **Changes:**
   - Added simple TypeScript utility functions
   - Added comprehensive tests

   **Expected outcome:**
   - ✅ TypeScript: 20/20
   - ✅ ESLint: 20/20
   - ✅ Tests: 20/20
   - ✅ Bundle: 20/20
   - ✅ Verdict: PASS
   - 🤖 Auto-merge to main

   ## Evidence
   Local verification:
   - `npx tsc --noEmit` ✅
   - `npx eslint .` ✅
   - `npm test` ✅

   ## Checklist
   - [x] All hard gates pass locally
   - [x] Tests validate behavior
   - [x] No new dependencies
   BODY
   )" \
     --base main
   ```

7. **Watch CI:**
   ```bash
   gh pr checks <PR_NUMBER> --watch
   ```

8. **Verify auto-merge:**
   ```bash
   # Wait for CI to complete
   sleep 30

   # Check if merged
   gh pr view <PR_NUMBER>
   # Should show: "Status: Merged"
   ```

9. **Check leaderboard:**
   ```bash
   gh browse --branch leaderboard LEADERBOARD.md
   # Or:
   curl -s https://raw.githubusercontent.com/<owner>/<repo>/leaderboard/LEADERBOARD.md
   ```

---

### Scenario 4: Path C — Implementation (Human Review)

**Objective:** Test implementation PR that needs human review due to new dependency.

**Steps:**

1. **Create test branch:**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b test/implement-with-dep
   ```

2. **Add a new dependency:**
   ```bash
   # Backup package.json
   cp package.json package.json.bak

   # Add a harmless dependency (e.g., lodash)
   npm install lodash
   ```

3. **Create code that uses it:**
   ```bash
   mkdir -p src/utils
   cat > src/utils/lodash-test.ts <<'EOF'
   import _ from 'lodash';

   export function uniqueValues(arr: number[]): number[] {
     return _.uniq(arr);
   }
   EOF
   ```

4. **Add test:**
   ```bash
   cat > src/utils/__tests__/lodash-test.test.ts <<'EOF'
   import { uniqueValues } from '../lodash-test';

   describe('uniqueValues', () => {
     it('should return unique values', () => {
       expect(uniqueValues([1, 2, 2, 3, 3, 3])).toEqual([1, 2, 3]);
     });
   });
   EOF
   ```

5. **Commit and push:**
   ```bash
   git add .
   git commit -m "feat(utils): add lodash utility (needs review)"
   git push -u origin test/implement-with-dep
   ```

6. **Create PR:**
   ```bash
   gh pr create \
     --title "feat(utils): add lodash utility (needs review)" \
     --body "$(cat <<'BODY'
   ## Test PR for Path C (Human Review Required)

   This PR adds a new dependency, which triggers human review.

   **Changes:**
   - Added lodash dependency
   - Added utility function using lodash

   **Expected outcome:**
   - ✅ Hard gates pass
   - ⏸️  Verdict: REVIEW (new dependency detected)
   - 👤 Waits for maintainer approval
   - Max score: 80 + 20 = 100pt (if maintainer assigns subjective score)

   ## Dependency justification
   Lodash provides battle-tested utility functions. This is a test PR.

   ## Evidence
   Local tests pass.
   BODY
   )" \
     --base main
   ```

7. **Watch CI:**
   ```bash
   gh pr checks <PR_NUMBER> --watch
   ```

8. **Verify REVIEW verdict:**
   ```bash
   gh pr view <PR_NUMBER>
   # Should see comment with ⏸️ REVIEW verdict
   ```

9. **Maintainer assigns score (if you're the maintainer):**
   ```bash
   gh pr comment <PR_NUMBER> --body "/score 18"
   ```

10. **Maintainer merges:**
    ```bash
    gh pr merge <PR_NUMBER> --squash
    ```

11. **Check leaderboard for combined score:**
    ```bash
    # Should show: 80 (objective) + 18 (subjective) = 98pt
    ```

---

### Scenario 5: Path C — Implementation (Failure)

**Objective:** Test implementation PR with TypeScript errors → CI blocks.

**Steps:**

1. **Create test branch:**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b test/implement-broken
   ```

2. **Create TypeScript file with intentional error:**
   ```bash
   mkdir -p src/utils
   cat > src/utils/broken.ts <<'EOF'
   /**
    * Intentionally broken TypeScript
    */
   export function brokenFunction(): string {
     const num: number = 42;
     return num;  // Type error: number is not assignable to string
   }
   EOF
   ```

3. **Verify error locally:**
   ```bash
   npx tsc --noEmit
   # Should show error
   ```

4. **Commit and push anyway (for testing):**
   ```bash
   git add src/
   git commit -m "feat(utils): add broken function (should fail CI)"
   git push -u origin test/implement-broken
   ```

5. **Create PR:**
   ```bash
   gh pr create \
     --title "feat(utils): add broken function (should fail)" \
     --body "Testing failure path. CI should block this PR." \
     --base main
   ```

6. **Watch CI fail:**
   ```bash
   gh pr checks <PR_NUMBER> --watch
   # Should show TypeScript check failing
   ```

7. **Verify FAIL verdict:**
   ```bash
   gh pr view <PR_NUMBER>
   # Should see comment with ❌ FAIL verdict and error details
   ```

8. **Cleanup:**
   ```bash
   gh pr close <PR_NUMBER>
   git checkout main
   git branch -D test/implement-broken
   git push origin --delete test/implement-broken
   ```

---

## Automated Test Script

For automated testing, use:

```bash
chmod +x scripts/test_workflows.sh
./scripts/test_workflows.sh
```

---

## Troubleshooting

### CI not triggering

**Problem:** PR created but no CI workflows run.

**Solution:**
1. Check if workflows are enabled: `gh repo view --web` → Actions tab
2. Verify workflow files exist: `ls -la .github/workflows/`
3. Check workflow triggers match PR target branch

### Auto-merge not working

**Problem:** CI passes but PR doesn't auto-merge.

**Solution:**
1. Check CI verdict: `gh pr view <PR_NUMBER>` (should say ✅ PASS)
2. Verify `auto-merge` job ran: `gh run list --workflow=evaluation.yml`
3. Check permissions in workflow file (needs `contents: write`)
4. Manually trigger: `gh workflow run evaluation.yml`

### Leaderboard not updating

**Problem:** PR merged but leaderboard branch not updated.

**Solution:**
1. Check if leaderboard branch exists: `git ls-remote origin leaderboard`
2. If not, create it: `git checkout --orphan leaderboard && git rm -rf . && git push origin leaderboard`
3. Re-run workflow manually

---

## Monitoring

### View all workflow runs:
```bash
gh run list --limit 20
```

### View specific run logs:
```bash
gh run view <RUN_ID> --log
```

### View PR comments:
```bash
gh pr view <PR_NUMBER> --comments
```

### View leaderboard:
```bash
gh browse --branch leaderboard LEADERBOARD.md
```

---

## Next Steps

After testing all scenarios:
1. Document any issues found
2. Update workflow.md if logic needs clarification
3. Update .github/workflows/*.yml if implementation needs fixes
4. Repeat tests to verify fixes
