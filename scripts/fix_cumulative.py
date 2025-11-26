#!/usr/bin/env python3
"""
Fix cumulative database by properly tracking what was already counted
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
CUMULATIVE_DB = Path.home() / ".claude" / "cumulative_usage.json"

# Historical peak (Nov 21, 2025 22:04)
PEAK_DATE = datetime(2025, 11, 21, 22, 4, 0, tzinfo=timezone.utc)
CUTOFF_DATE = datetime(2025, 10, 1, tzinfo=timezone.utc)

HISTORICAL_PEAK = {
    "input_tokens": 122396,
    "output_tokens": 2615355,
    "cache_creation_tokens": 45201785,
    "cache_read_tokens": 351620275,
    "total_sessions": 5035
}

def create_session_id(file_path, timestamp, usage_data):
    """Create unique session ID"""
    unique_str = f"{file_path.name}_{timestamp}_{usage_data.get('input_tokens', 0)}_{usage_data.get('output_tokens', 0)}"
    return hashlib.md5(unique_str.encode()).hexdigest()

def scan_and_mark_old_sessions():
    """Scan all sessions and mark those before peak date as processed"""
    print("🔍 Scanning for sessions before Nov 21, 2025 22:04...")
    print()

    jsonl_files = list(PROJECT_DIR.glob("**/*.jsonl"))

    old_sessions = {}  # Sessions before peak
    new_sessions = {}  # Sessions after peak

    old_count = 0
    new_count = 0

    for jsonl_file in jsonl_files:
        try:
            with open(jsonl_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip():
                        continue

                    try:
                        data = json.loads(line)

                        if 'timestamp' not in data:
                            continue

                        timestamp_str = data['timestamp']
                        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))

                        # Skip sessions before cutoff
                        if timestamp < CUTOFF_DATE:
                            continue

                        if 'message' not in data or 'usage' not in data['message']:
                            continue

                        usage = data['message']['usage']
                        session_id = create_session_id(jsonl_file, timestamp_str, usage)

                        session_data = {
                            "file": jsonl_file.name,
                            "timestamp": timestamp_str,
                            "input_tokens": usage.get('input_tokens', 0),
                            "output_tokens": usage.get('output_tokens', 0),
                            "cache_creation_tokens": usage.get('cache_creation_input_tokens', 0),
                            "cache_read_tokens": usage.get('cache_read_input_tokens', 0)
                        }

                        if timestamp <= PEAK_DATE:
                            old_sessions[session_id] = session_data
                            old_count += 1
                        else:
                            new_sessions[session_id] = session_data
                            new_count += 1

                    except json.JSONDecodeError:
                        continue

        except Exception as e:
            continue

    print(f"✅ Found {old_count:,} sessions BEFORE peak (Nov 21)")
    print(f"✅ Found {new_count:,} sessions AFTER peak")
    print()

    return old_sessions, new_sessions

def calculate_new_tokens(new_sessions):
    """Calculate tokens from new sessions"""
    tokens = {
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_creation_tokens": 0,
        "cache_read_tokens": 0
    }

    for session_data in new_sessions.values():
        tokens["input_tokens"] += session_data["input_tokens"]
        tokens["output_tokens"] += session_data["output_tokens"]
        tokens["cache_creation_tokens"] += session_data["cache_creation_tokens"]
        tokens["cache_read_tokens"] += session_data["cache_read_tokens"]

    return tokens

def create_fixed_database(old_sessions, new_sessions, new_tokens):
    """Create properly fixed database"""

    # Combine old and new processed sessions
    all_processed = {**old_sessions, **new_sessions}

    # Calculate cumulative totals (peak + new)
    cumulative = {
        "input_tokens": HISTORICAL_PEAK["input_tokens"] + new_tokens["input_tokens"],
        "output_tokens": HISTORICAL_PEAK["output_tokens"] + new_tokens["output_tokens"],
        "cache_creation_tokens": HISTORICAL_PEAK["cache_creation_tokens"] + new_tokens["cache_creation_tokens"],
        "cache_read_tokens": HISTORICAL_PEAK["cache_read_tokens"] + new_tokens["cache_read_tokens"],
        "total_sessions": HISTORICAL_PEAK["total_sessions"] + len(new_sessions)
    }

    db = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "period_start": "2025-10-01",
        "restored_from_peak": "2025-11-21",
        "cumulative_usage": cumulative,
        "processed_sessions": all_processed,
        "run_history": [
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "action": "fixed_database_with_proper_session_tracking",
                "peak_sessions": HISTORICAL_PEAK["total_sessions"],
                "new_sessions": len(new_sessions),
                "total_sessions": cumulative["total_sessions"]
            }
        ]
    }

    return db

def main():
    """Main execution"""
    print()
    print("=" * 70)
    print("🔧 FIXING CUMULATIVE DATABASE")
    print("=" * 70)
    print()

    # Backup current
    if CUMULATIVE_DB.exists():
        backup_file = CUMULATIVE_DB.parent / f"cumulative_usage_before_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(CUMULATIVE_DB, 'r', encoding='utf-8') as f:
            data = json.load(f)
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Backed up current database to: {backup_file}")
        print()

    # Scan sessions
    old_sessions, new_sessions = scan_and_mark_old_sessions()

    # Calculate new tokens
    new_tokens = calculate_new_tokens(new_sessions)

    print("📊 New sessions since Nov 21:")
    print(f"   Count:          {len(new_sessions):,}")
    print(f"   Input:          {new_tokens['input_tokens']:,}")
    print(f"   Output:         {new_tokens['output_tokens']:,}")
    print(f"   Cache Creation: {new_tokens['cache_creation_tokens']:,}")
    print(f"   Cache Read:     {new_tokens['cache_read_tokens']:,}")
    print()

    # Create fixed database
    db = create_fixed_database(old_sessions, new_sessions, new_tokens)

    cumulative = db["cumulative_usage"]
    total_processed = (
        cumulative["input_tokens"] +
        cumulative["output_tokens"] +
        cumulative["cache_creation_tokens"]
    )

    print("=" * 70)
    print("✅ FIXED CUMULATIVE TOTALS")
    print("=" * 70)
    print()
    print(f"📊 Total Sessions: {cumulative['total_sessions']:,}")
    print()
    print(f"🔢 TOKEN TOTALS:")
    print(f"   Input:          {cumulative['input_tokens']:,}")
    print(f"   Output:         {cumulative['output_tokens']:,}")
    print(f"   Cache Creation: {cumulative['cache_creation_tokens']:,}")
    print(f"   Cache Read:     {cumulative['cache_read_tokens']:,}")
    print()
    print(f"💰 TOTAL PROCESSED: {total_processed:,} tokens ({total_processed/1_000_000:.2f}M)")
    print()

    # Calculate cost
    input_cost = (cumulative['input_tokens'] / 1_000_000) * 3.0
    output_cost = (cumulative['output_tokens'] / 1_000_000) * 15.0
    cache_write_cost = (cumulative['cache_creation_tokens'] / 1_000_000) * 3.75
    cache_read_cost = (cumulative['cache_read_tokens'] / 1_000_000) * 0.30
    total_cost = input_cost + output_cost + cache_write_cost + cache_read_cost

    print(f"💵 ESTIMATED COST: ${total_cost:.2f}")
    print()
    print("=" * 70)

    # Save database
    with open(CUMULATIVE_DB, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)

    print()
    print(f"✅ Database saved to: {CUMULATIVE_DB}")
    print()
    print("🎉 Database is now FIXED and properly tracking all sessions!")
    print()

if __name__ == "__main__":
    main()
