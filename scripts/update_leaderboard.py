#!/usr/bin/env python3
"""
Update LEADERBOARD.md with new submission results.

This script is called by .github/workflows/evaluation.yml after scoring a PR.
It reads the existing leaderboard, adds the new submission, updates rankings,
and writes the updated leaderboard to /tmp/LEADERBOARD.md.
"""

import argparse
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Update Nokta leaderboard")
    parser.add_argument("--username", required=True, help="GitHub username")
    parser.add_argument("--pr-number", required=True, help="PR number")
    parser.add_argument("--score", required=True, type=float, help="Objective score (0-80)")
    parser.add_argument("--verdict", required=True, help="PASS, REVIEW, or FAIL")
    parser.add_argument("--merge-type", required=True, help="AUTO or HUMAN")
    parser.add_argument("--typescript-score", required=True, type=int, help="TypeScript score")
    parser.add_argument("--eslint-score", required=True, type=int, help="ESLint score")
    parser.add_argument("--test-score", required=True, type=int, help="Test score")
    parser.add_argument("--bundle-score", required=True, type=int, help="Bundle size score")
    parser.add_argument("--golden-score", required=True, type=float, help="Golden flow score")
    parser.add_argument("--subjective-score", type=int, default=0, help="Subjective score (0-20, human review only)")
    return parser.parse_args()


def read_leaderboard() -> Tuple[List[str], List[Dict], List[Dict]]:
    """
    Read existing leaderboard from leaderboard branch or create empty one.

    Returns:
        header_lines: Lines before the submissions table
        leaders: List of leader entries
        submissions: List of submission entries
    """
    leaderboard_path = Path("/tmp/lb-worktree/LEADERBOARD.md")

    if not leaderboard_path.exists():
        # Return empty structure
        return [], [], []

    content = leaderboard_path.read_text()

    # Parse existing submissions
    submissions = []
    leaders = {}

    # Extract submissions table
    submissions_match = re.search(
        r"## All Submissions\s*\n\s*\| PR \|.*?\n\|[-|]+\|\s*\n(.*?)\n\n",
        content,
        re.DOTALL
    )

    if submissions_match:
        submissions_text = submissions_match.group(1).strip()
        if submissions_text and not submissions_text.startswith("*No submissions"):
            for line in submissions_text.split("\n"):
                if line.strip().startswith("|"):
                    parts = [p.strip() for p in line.split("|")[1:-1]]  # Remove empty first/last
                    if len(parts) >= 11:
                        pr_num = parts[0].strip("#")
                        username = parts[1].strip("@")
                        score = float(parts[2])

                        submission = {
                            "pr": pr_num,
                            "username": username,
                            "score": score,
                            "verdict": parts[3],
                            "typescript": parts[4],
                            "eslint": parts[5],
                            "tests": parts[6],
                            "bundle": parts[7],
                            "deps": parts[8],
                            "golden": parts[9],
                            "date": parts[10],
                        }
                        submissions.append(submission)

                        # Track best score per contributor
                        if username not in leaders or score > leaders[username]["score"]:
                            leaders[username] = {
                                "username": username,
                                "score": score,
                                "pr_count": 0,
                                "best_pr": pr_num,
                            }

    # Count PRs per contributor
    for submission in submissions:
        username = submission["username"]
        if username in leaders:
            leaders[username]["pr_count"] += 1

    return content, list(leaders.values()), submissions


def add_submission(
    username: str,
    pr_number: str,
    objective_score: float,
    subjective_score: int,
    verdict: str,
    merge_type: str,
    typescript_score: int,
    eslint_score: int,
    test_score: int,
    bundle_score: int,
    golden_score: float,
    submissions: List[Dict],
    leaders: List[Dict],
) -> Tuple[List[Dict], List[Dict]]:
    """
    Add new submission and update leaders.

    Returns:
        Updated (leaders, submissions) tuple
    """
    now = datetime.utcnow().strftime("%Y-%m-%d")
    total_score = objective_score + subjective_score

    # Emoji mapping
    def score_to_emoji(score, max_score):
        if score == max_score:
            return "✅"
        elif score >= max_score * 0.5:
            return "⚠️"
        else:
            return "❌"

    # Verdict emoji
    if verdict == "PASS":
        verdict_emoji = "✅ AUTO"
    elif verdict == "REVIEW":
        verdict_emoji = "⏸️  REVIEW"
    else:
        verdict_emoji = "❌ FAIL"

    # Merge type
    merge_badge = "🤖" if merge_type == "AUTO" else "👤"

    new_submission = {
        "pr": pr_number,
        "username": username,
        "total_score": total_score,
        "objective": objective_score,
        "subjective": subjective_score,
        "verdict": verdict_emoji,
        "merge_type": merge_badge,
        "typescript": score_to_emoji(typescript_score, 20),
        "eslint": score_to_emoji(eslint_score, 20),
        "tests": score_to_emoji(test_score, 20),
        "bundle": score_to_emoji(bundle_score, 20),
        "golden": score_to_emoji(golden_score, 10),
        "date": now,
    }

    submissions.append(new_submission)

    # Update leaders (only if not FAIL)
    if verdict != "FAIL":
        leader = next((l for l in leaders if l["username"] == username), None)
        if leader:
            leader["pr_count"] += 1
            if total_score > leader["score"]:
                leader["score"] = total_score
                leader["best_pr"] = pr_number
            # Update latest
            leader["latest"] = now
        else:
            leaders.append({
                "username": username,
                "score": total_score,
                "pr_count": 1,
                "best_pr": pr_number,
                "latest": now,
            })

    # Sort leaders by score (descending)
    leaders.sort(key=lambda x: x["score"], reverse=True)

    # Sort submissions by date (descending)
    submissions.sort(key=lambda x: x["date"], reverse=True)

    return leaders, submissions


def generate_leaderboard(leaders: List[Dict], submissions: List[Dict]) -> str:
    """Generate updated LEADERBOARD.md content."""
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    content = """# 🏆 Nokta Leaderboard

This leaderboard tracks all evaluated implementation contributions (Path C). Scores are automatically calculated by CI based on:

- **TypeScript** (20pt) — Zero compilation errors
- **ESLint** (20pt) — Zero linting errors
- **Tests** (20pt) — All tests passing
- **Bundle Size** (20pt) — JS bundle < 2MB
- **Dependencies** (10pt) — No unauthorized changes
- **Golden Flows** (10pt) — Integration tests passing

**Total:** 100 points maximum

---

## Current Leaders

| Rank | Contributor | Total Score | PRs | Best PR | Latest |
|------|-------------|-------------|-----|---------|--------|
"""

    if not leaders:
        content += "| - | - | - | - | - | - |\n\n*No submissions yet. Be the first!*\n"
    else:
        for rank, leader in enumerate(leaders, 1):
            medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"{rank}."
            content += f"| {medal} | @{leader['username']} | **{leader['score']:.1f}** | {leader['pr_count']} | #{leader['best_pr']} | {leader.get('latest', 'N/A')} |\n"

    content += """
---

## All Submissions

| PR | Contributor | Total | Obj | Subj | Verdict | Type | TS | Lint | Test | Bundle | Golden | Date |
|----|-------------|-------|-----|------|---------|------|----|----|------|--------|--------|------|
"""

    if not submissions:
        content += "\n*No submissions yet.*\n"
    else:
        for sub in submissions:
            content += f"| #{sub['pr']} | @{sub['username']} | **{sub['total_score']:.1f}** | {sub['objective']:.0f} | {sub['subjective']} | {sub['verdict']} | {sub['merge_type']} | {sub['typescript']} | {sub['eslint']} | {sub['tests']} | {sub['bundle']} | {sub['golden']} | {sub['date']} |\n"

    content += f"""
---

## Scoring Rules

- **Hard Gates:** TypeScript, ESLint, Tests, Bundle Size must PASS (no ❌) for PR to be eligible for review
- **Verdict:**
  - ✅ **PASS** — Eligible for human review (may be merged)
  - ❌ **FAIL** — One or more hard gates failed (must fix and resubmit)
- **Leaderboard Ranking:** Based on highest total score achieved in any single PR
- **Multiple PRs:** Contributors can submit multiple PRs; only the best score counts for ranking

---

## How to Contribute

See [README.md](README.md#path-c--implement-code-from-specs-implementation) for Path C instructions.

1. Read an approved spec (`program.md` or `specs/*.md`)
2. Implement the feature exactly as specified
3. Run hard gates locally before opening PR
4. Open PR to `submissions` branch
5. CI runs evaluation and posts scorecard
6. If PASS, wait for maintainer review
7. If FAIL, fix issues and push again

---

**Last Updated:** {now}

**Total Contributors:** {len(leaders)}

**Total Submissions:** {len(submissions)}

---

🤖 Auto-generated by Nokta Evaluation CI
"""

    return content


def main():
    args = parse_args()

    # Read existing leaderboard
    content, leaders, submissions = read_leaderboard()

    # Calculate total score
    total_score = args.score + args.subjective_score

    # Add new submission
    leaders, submissions = add_submission(
        username=args.username,
        pr_number=args.pr_number,
        objective_score=args.score,
        subjective_score=args.subjective_score,
        verdict=args.verdict,
        merge_type=args.merge_type,
        typescript_score=args.typescript_score,
        eslint_score=args.eslint_score,
        test_score=args.test_score,
        bundle_score=args.bundle_score,
        golden_score=args.golden_score,
        submissions=submissions,
        leaders=leaders,
    )

    # Generate updated leaderboard
    updated_content = generate_leaderboard(leaders, submissions)

    # Write to /tmp/LEADERBOARD.md
    output_path = Path("/tmp/LEADERBOARD.md")
    output_path.write_text(updated_content)

    print(f"✅ Leaderboard updated: {len(submissions)} total submissions, {len(leaders)} contributors")
    print(f"   New submission: @{args.username} #{args.pr_number} — {total_score:.1f}/100 ({args.score:.0f} obj + {args.subjective_score} subj) [{args.verdict}]")


if __name__ == "__main__":
    main()
