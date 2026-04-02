#!/usr/bin/env python3
"""
agent_reviewer.py — Nokta Constitution Reviewer

Evaluates open PRs against program.md, generates feedback, and updates 
the decision ledger. Integrates with 'gh' CLI.
"""

import os
import json
import yaml
import subprocess
import argparse
from datetime import datetime

# Path constants
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROGRAM_MD = os.path.join(BASE_DIR, "program.md")
LEDGER_PATH = os.path.join(BASE_DIR, "scripts", "pr_decision_ledger.yml")

def run_command(cmd, cwd=BASE_DIR):
    """Run a shell command and return output."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        print(f"Error running command: {cmd}\n{result.stderr}")
        return None
    return result.stdout.strip()

def get_open_prs():
    """Get list of open PRs via gh CLI."""
    out = run_command("gh pr list --limit 100 --json number,title,author,body,url")
    if not out:
        return []
    return json.loads(out)

def get_pr_diff(pr_number):
    """Get PR diff via gh CLI."""
    return run_command(f"gh pr diff {pr_number}")

def load_ledger():
    if not os.path.exists(LEDGER_PATH):
        return []
    with open(LEDGER_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        return data if data else []

def save_ledger(ledger):
    with open(LEDGER_PATH, "w", encoding="utf-8") as f:
        yaml.dump(ledger, f, default_flow_style=False, sort_keys=False)

def main():
    parser = argparse.ArgumentParser(description="Nokta PR Reviewer")
    parser.add_argument("--limit", type=int, default=5, help="Limit number of PRs to process")
    parser.add_argument("--dry-run", action="store_true", help="Don't post comments or merge")
    args = parser.parse_args()

    ledger = load_ledger()
    reviewed_ids = {item["pr_number"] for item in ledger}
    
    prs = get_open_prs()
    to_process = [pr for pr in prs if pr["number"] not in reviewed_ids][:args.limit]

    print(f"Loaded {len(prs)} open PRs. Skipping {len(reviewed_ids)} already in ledger.")
    print(f"Found {len(to_process)} PRs to process.")

    for pr in to_process:
        num = pr["number"]
        print(f"\n--- Processing PR #{num}: {pr['title']} ---")
        
        diff = get_pr_diff(num)
        if not diff:
            print("Skipping due to empty diff.")
            continue

        # This is where the LLM logic would go. 
        # Since I (the assistant) am the one running this, I will manually 
        # simulate the LLM call for the first batch or use an LLM API if available.
        # For now, I'll provide a placeholder or return to the user.
        print(f"Read diff: {len(diff)} characters.")
        
        # In a real CI environment, this would call an LLM API.
        # But here, Antigravity will do the evaluation.
        
    print("\nBatch complete.")

if __name__ == "__main__":
    main()
