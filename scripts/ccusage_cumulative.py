#!/usr/bin/env python3
"""
Cumulative Claude usage tracker - NEVER loses token counts even if files are deleted

Key features:
- Tracks each session with unique ID (file + timestamp)
- Stores processed sessions in permanent database
- New runs only add NEW sessions to cumulative total
- Deleted files don't affect cumulative count

Created & Directed by Bohee Lee
https://github.com/bohee-connectome

Built with Claude Code
"""

import sys
import io
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path

# Set UTF-8 encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Paths
PROJECT_DIR = Path.home() / ".claude" / "projects"
DB_FILE = Path.home() / ".claude" / "cumulative_usage.json"
CUTOFF_DATE = datetime(2025, 10, 1, tzinfo=timezone.utc)

def load_database():
    """Load cumulative usage database"""
    if DB_FILE.exists():
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)

    # Initialize new database
    return {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "period_start": "2025-10-01",
        "cumulative_usage": {
            "input_tokens": 0,
            "output_tokens": 0,
            "cache_creation_tokens": 0,
            "cache_read_tokens": 0,
            "total_sessions": 0
        },
        "processed_sessions": {},  # session_id -> {tokens, timestamp}
        "run_history": []
    }

def save_database(db):
    """Save cumulative usage database"""
    db["last_updated"] = datetime.now(timezone.utc).isoformat()

    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Database saved to: {DB_FILE}")

def create_session_id(file_path, timestamp, usage_data):
    """Create unique session ID"""
    # Use file name + timestamp + first few token counts as unique identifier
    unique_str = f"{file_path.name}_{timestamp}_{usage_data.get('input_tokens', 0)}_{usage_data.get('output_tokens', 0)}"
    return hashlib.md5(unique_str.encode()).hexdigest()

def scan_sessions(db):
    """Scan for new sessions and add to cumulative total"""
    jsonl_files = list(PROJECT_DIR.glob("**/*.jsonl"))

    new_sessions = 0
    new_tokens = {
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_creation_tokens": 0,
        "cache_read_tokens": 0
    }

    processed_sessions = db.get("processed_sessions", {})

    print(f"🔍 Scanning {len(jsonl_files)} JSONL files...")
    print(f"📊 Previously processed sessions: {len(processed_sessions)}")
    print()

    # Process each file
    for jsonl_file in jsonl_files:
        try:
            with open(jsonl_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip():
                        continue

                    try:
                        data = json.loads(line)

                        # Check timestamp
                        if 'timestamp' in data:
                            timestamp_str = data['timestamp']
                            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))

                            # Only count from October 1, 2025 onwards
                            if timestamp < CUTOFF_DATE:
                                continue
                        else:
                            continue

                        # Extract usage
                        if 'message' in data and 'usage' in data['message']:
                            usage = data['message']['usage']

                            # Create unique session ID
                            session_id = create_session_id(jsonl_file, timestamp_str, usage)

                            # Skip if already processed
                            if session_id in processed_sessions:
                                continue

                            # New session found!
                            session_data = {
                                "file": jsonl_file.name,
                                "timestamp": timestamp_str,
                                "input_tokens": usage.get('input_tokens', 0),
                                "output_tokens": usage.get('output_tokens', 0),
                                "cache_creation_tokens": usage.get('cache_creation_input_tokens', 0),
                                "cache_read_tokens": usage.get('cache_read_input_tokens', 0)
                            }

                            # Add to processed sessions
                            processed_sessions[session_id] = session_data

                            # Add to new tokens count
                            new_tokens["input_tokens"] += session_data["input_tokens"]
                            new_tokens["output_tokens"] += session_data["output_tokens"]
                            new_tokens["cache_creation_tokens"] += session_data["cache_creation_tokens"]
                            new_tokens["cache_read_tokens"] += session_data["cache_read_tokens"]

                            new_sessions += 1

                    except json.JSONDecodeError:
                        continue

        except Exception as e:
            print(f"⚠️  Error reading {jsonl_file.name}: {e}")
            continue

    # Update database
    db["processed_sessions"] = processed_sessions

    # Add new tokens to cumulative total
    cumulative = db["cumulative_usage"]
    cumulative["input_tokens"] += new_tokens["input_tokens"]
    cumulative["output_tokens"] += new_tokens["output_tokens"]
    cumulative["cache_creation_tokens"] += new_tokens["cache_creation_tokens"]
    cumulative["cache_read_tokens"] += new_tokens["cache_read_tokens"]
    cumulative["total_sessions"] += new_sessions

    return new_sessions, new_tokens

def calculate_cost(usage):
    """Calculate estimated cost"""
    input_cost = (usage["input_tokens"] / 1_000_000) * 3.0
    output_cost = (usage["output_tokens"] / 1_000_000) * 15.0
    cache_write_cost = (usage["cache_creation_tokens"] / 1_000_000) * 3.75
    cache_read_cost = (usage["cache_read_tokens"] / 1_000_000) * 0.30
    return input_cost + output_cost + cache_write_cost + cache_read_cost

def display_results(db, new_sessions, new_tokens):
    """Display cumulative results"""
    cumulative = db["cumulative_usage"]

    print("=" * 70)
    print("📈 CUMULATIVE CLAUDE USAGE (PERMANENT RECORD)")
    print(f"Period: October 1, 2025 - {datetime.now().strftime('%B %d, %Y')}")
    print("=" * 70)
    print()

    if new_sessions > 0:
        print(f"🆕 NEW SESSIONS THIS RUN:  {new_sessions:,}")
        print(f"   Input:          {new_tokens['input_tokens']:,}")
        print(f"   Output:         {new_tokens['output_tokens']:,}")
        print(f"   Cache Creation: {new_tokens['cache_creation_tokens']:,}")
        print(f"   Cache Read:     {new_tokens['cache_read_tokens']:,}")
        new_cost = calculate_cost(new_tokens)
        print(f"   Cost:           ${new_cost:.2f}")
        print()
    else:
        print("✅ No new sessions found (all sessions already counted)")
        print()

    print(f"📊 CUMULATIVE TOTAL SESSIONS: {cumulative['total_sessions']:,}")
    print()
    print("🔢 CUMULATIVE TOKEN TOTALS:")
    print(f"  Input Tokens:        {cumulative['input_tokens']:,}")
    print(f"  Output Tokens:       {cumulative['output_tokens']:,}")
    print(f"  Cache Creation:      {cumulative['cache_creation_tokens']:,}")
    print(f"  Cache Read:          {cumulative['cache_read_tokens']:,}")
    print()

    total_cost = calculate_cost(cumulative)

    print("💵 CUMULATIVE ESTIMATED COST (Sonnet 4.5):")
    input_cost = (cumulative['input_tokens'] / 1_000_000) * 3.0
    output_cost = (cumulative['output_tokens'] / 1_000_000) * 15.0
    cache_write_cost = (cumulative['cache_creation_tokens'] / 1_000_000) * 3.75
    cache_read_cost = (cumulative['cache_read_tokens'] / 1_000_000) * 0.30

    print(f"  Input:        ${input_cost:.2f}")
    print(f"  Output:       ${output_cost:.2f}")
    print(f"  Cache Write:  ${cache_write_cost:.2f}")
    print(f"  Cache Read:   ${cache_read_cost:.2f}")
    print()
    print(f"  TOTAL:        ${total_cost:.2f}")
    print()
    print("=" * 70)
    print()
    print("ℹ️  Database location: " + str(DB_FILE))
    print("⚠️  This count is CUMULATIVE and PERMANENT")
    print("   Even if .jsonl files are deleted, counts remain!")
    print("=" * 70)

def main():
    """Main execution"""
    print("🚀 Cumulative Claude Usage Tracker")
    print()

    # Load database
    db = load_database()

    # Scan for new sessions
    new_sessions, new_tokens = scan_sessions(db)

    # Add run history
    if "run_history" not in db:
        db["run_history"] = []

    db["run_history"].append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "new_sessions": new_sessions,
        "new_tokens": new_tokens
    })

    # Keep only last 100 runs in history
    db["run_history"] = db["run_history"][-100:]

    # Save database
    save_database(db)

    # Display results
    display_results(db, new_sessions, new_tokens)

if __name__ == "__main__":
    main()
