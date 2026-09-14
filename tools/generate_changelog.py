#!/usr/bin/env python3
"""
tools/generate_changelog.py

Automated changelog generator for TortoiseBots.
Pulls merged PRs from GitHub since the last tag or CHANGELOG entry,
uses an OpenCode / OpenAI-compatible model (e.g. DeepSeek) to summarize them
into human-readable gamer-friendly notes, and optionally updates CHANGELOG.md
and outputs release notes for GitHub Releases.

Usage:
  export OPENCODE_API_KEY="sk-..."
  python3 tools/generate_changelog.py [--dry-run] [--write] [--out-notes notes.md]
"""

import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import urllib.request
import urllib.error

DEFAULT_BASE_URL = os.environ.get("OPENCODE_BASE_URL", "https://opencode.ai/zen/go/v1")
DEFAULT_MODEL = os.environ.get("OPENCODE_MODEL", "deepseek-v4.1-flash")
CHANGELOG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "CHANGELOG.md")


def get_last_release_info():
    """Find the date/tag of the latest release or latest section in CHANGELOG.md."""
    # 1. Try to get latest tag via git
    try:
        tag = subprocess.check_output(
            ["git", "describe", "--tags", "--abbrev=0"],
            stderr=subprocess.DEVNULL,
            text=True
        ).strip()
        tag_date = subprocess.check_output(
            ["git", "log", "-1", "--format=%cI", tag],
            stderr=subprocess.DEVNULL,
            text=True
        ).strip()
        return tag, tag_date
    except Exception:
        pass

    # 2. Try to read CHANGELOG.md for the most recent date header (e.g. ## 2026-09-14)
    if os.path.exists(CHANGELOG_PATH):
        with open(CHANGELOG_PATH, "r", encoding="utf-8") as f:
            for line in f:
                m = re.match(r"^##\s+(\d{4}-\d{2}-\d{2})", line)
                if m:
                    # Convert to ISO datetime at start of day
                    date_str = m.group(1)
                    return date_str, f"{date_str}T00:00:00Z"

    return None, None


def get_merged_prs_since(since_iso_date=None):
    """Retrieve merged pull requests using the gh CLI."""
    cmd = [
        "gh", "pr", "list",
        "--state", "merged",
        "--base", "main",
        "--limit", "100",
        "--json", "number,title,body,mergedAt,author,url"
    ]
    try:
        output = subprocess.check_output(cmd, text=True)
        prs = json.loads(output)
    except Exception as e:
        print(f"Error fetching PRs via gh CLI: {e}", file=sys.stderr)
        return []

    if not since_iso_date:
        return prs

    # Filter by mergedAt > since_iso_date
    filtered = []
    for pr in prs:
        merged_at = pr.get("mergedAt")
        if merged_at and merged_at > since_iso_date:
            filtered.append(pr)

    return filtered


def generate_summary_with_ai(prs, api_key, base_url, model):
    """Send PR metadata to OpenCode / OpenAI-compatible endpoint for summarization."""
    pr_summaries = []
    for pr in prs:
        body = (pr.get("body") or "").strip()
        # Truncate long bodies to avoid token limits
        if len(body) > 600:
            body = body[:600] + "..."
        author = pr.get("author", {}).get("login", "unknown")
        pr_summaries.append(
            f"- PR #{pr['number']}: {pr['title']} (by @{author})\n  Details: {body}"
        )

    pr_text = "\n\n".join(pr_summaries)

    system_prompt = (
        "You are an assistant generating release notes and changelog entries for TortoiseBots, "
        "an optional native PlayerBots C++ module for Tortoise WoW 1.18.1.\n"
        "Your audience consists of players, guild leaders, and private server operators.\n"
        "Rules:\n"
        "1. Group changes into clear, logical categories (e.g., 'Combat & AI', 'Starter Zones & World', 'Observability & Engine', 'Core Sync & Fixes'). Only include categories that have changes.\n"
        "2. Write concise, punchy, pragmatic bullet points explaining the gameplay or stability impact.\n"
        "3. Always reference the pull request number like (#123) at the end of each bullet point.\n"
        "4. Do NOT output fluff, introductions, greetings, or sign-offs. Output ONLY the categorized markdown bullets starting with category headers (### Category).\n"
        "5. Keep the tone pragmatic and developer/gamer friendly."
    )

    user_prompt = f"Summarize the following merged pull requests:\n\n{pr_text}"

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.3
    }

    url = f"{base_url.rstrip('/')}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            content = data["choices"][0]["message"]["content"].strip()
            return content
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        raise RuntimeError(f"OpenCode API error ({e.code}): {error_body}")
    except Exception as e:
        raise RuntimeError(f"Failed to communicate with OpenCode API: {e}")


def prepend_to_changelog(date_str, summary_text):
    """Prepend the new release section to CHANGELOG.md."""
    header = f"## {date_str}\n\n{summary_text}\n\n"
    
    if os.path.exists(CHANGELOG_PATH):
        with open(CHANGELOG_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check if already has a main title
        if content.startswith("# Changelog"):
            parts = content.split("\n\n", 1)
            new_content = parts[0] + "\n\n" + header + (parts[1] if len(parts) > 1 else "")
        else:
            new_content = f"# Changelog\n\nAll notable changes to TortoiseBots are documented here.\n\n{header}{content}"
    else:
        new_content = f"# Changelog\n\nAll notable changes to TortoiseBots are documented here.\n\n{header}"

    with open(CHANGELOG_PATH, "w", encoding="utf-8") as f:
        f.write(new_content.strip() + "\n")
    print(f"Updated {CHANGELOG_PATH}")


def main():
    parser = argparse.ArgumentParser(description="Generate release notes from merged PRs using OpenCode AI.")
    parser.add_argument("--since", help="ISO timestamp or date to search PRs since (default: auto-detect from last tag/changelog)")
    parser.add_argument("--write", action="store_true", help="Prepend generated entry to CHANGELOG.md")
    parser.add_argument("--out-notes", help="Write release notes to specified file (useful for gh release create)")
    parser.add_argument("--dry-run", action="store_true", help="Print collected PRs without calling AI API")
    parser.add_argument("--date", default=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"), help="Release date string (default: today)")
    args = parser.parse_args()

    api_key = os.environ.get("OPENCODE_API_KEY")
    base_url = os.environ.get("OPENCODE_BASE_URL", DEFAULT_BASE_URL)
    model = os.environ.get("OPENCODE_MODEL", DEFAULT_MODEL)

    since_tag, since_date = None, None
    if args.since:
        since_date = args.since
    else:
        since_tag, since_date = get_last_release_info()

    print(f"Checking for merged PRs since: {since_date or 'beginning'} (reference: {since_tag or 'none'})")
    prs = get_merged_prs_since(since_date)

    if not prs:
        print("No new merged PRs found since last release/entry. Nothing to do.")
        # Set GitHub Action output if in GHA environment
        if "GITHUB_OUTPUT" in os.environ:
            with open(os.environ["GITHUB_OUTPUT"], "a") as gh_out:
                gh_out.write("has_changes=false\n")
        sys.exit(0)

    print(f"Found {len(prs)} merged PR(s) to summarize:")
    for pr in prs:
        print(f"  #{pr['number']}: {pr['title']}")

    if args.dry_run:
        print("\n[Dry Run] PRs collected successfully. Skipping AI API call.")
        sys.exit(0)

    if not api_key:
        print("Error: OPENCODE_API_KEY environment variable is required to generate AI summaries.", file=sys.stderr)
        sys.exit(1)

    print(f"\nRequesting AI summary from OpenCode ({model} @ {base_url})...")
    summary = generate_summary_with_ai(prs, api_key, base_url, model)
    print("\nGenerated Changelog:\n")
    print(summary)
    print("\n" + "=" * 40)

    if args.out_notes:
        with open(args.out_notes, "w", encoding="utf-8") as f:
            f.write(summary + "\n")
        print(f"Saved release notes to: {args.out_notes}")

    if args.write:
        prepend_to_changelog(args.date, summary)

    if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "a") as gh_out:
            gh_out.write("has_changes=true\n")
            gh_out.write(f"release_tag=v{args.date}\n")
            gh_out.write(f"release_title=TortoiseBots Update ({args.date})\n")


if __name__ == "__main__":
    main()
