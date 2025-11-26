#!/usr/bin/env python3
"""
Restore cumulative database from historical Git data

This fixes the problem where cumulative tracker started from scratch
and lost previous counts.
"""

import sys
import io
import json
from pathlib import Path
from datetime import datetime, timezone

# Set UTF-8 encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Paths
CUMULATIVE_DB = Path.home() / ".claude" / "cumulative_usage.json"
HISTORICAL_DATA = Path.home() / "claude-usage-tracker" / "data" / "yangpyungpc.json"

# Historical peak data (from Nov 21, 2025 - Git commit 482519c)
HISTORICAL_PEAK = {
    "input_tokens": 122396,
    "output_tokens": 2615355,
    "cache_creation_tokens": 45201785,
    "cache_read_tokens": 351620275,
    "total_sessions": 5035,
    "date": "2025-11-21",
    "cost": 314.59
}

def backup_current_db():
    """Backup current database"""
    if CUMULATIVE_DB.exists():
        backup_file = CUMULATIVE_DB.parent / f"cumulative_usage_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(CUMULATIVE_DB, 'r', encoding='utf-8') as f:
            data = json.load(f)

        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"✅ Backed up current database to: {backup_file}")
        return data

    return None

def restore_from_peak():
    """Restore cumulative database using historical peak"""
    print("=" * 70)
    print("🔧 RESTORING CUMULATIVE DATABASE FROM HISTORICAL PEAK")
    print("=" * 70)
    print()

    # Backup current
    current_db = backup_current_db()

    print()
    print("📊 Historical Peak (Nov 21, 2025):")
    print(f"   Total Sessions: {HISTORICAL_PEAK['total_sessions']:,}")
    print(f"   Input:          {HISTORICAL_PEAK['input_tokens']:,}")
    print(f"   Output:         {HISTORICAL_PEAK['output_tokens']:,}")
    print(f"   Cache Creation: {HISTORICAL_PEAK['cache_creation_tokens']:,}")
    print(f"   Cache Read:     {HISTORICAL_PEAK['cache_read_tokens']:,}")
    print(f"   Cost:           ${HISTORICAL_PEAK['cost']:.2f}")

    total_processed = (
        HISTORICAL_PEAK['input_tokens'] +
        HISTORICAL_PEAK['output_tokens'] +
        HISTORICAL_PEAK['cache_creation_tokens']
    )
    print(f"   TOTAL PROCESSED: {total_processed:,} tokens")
    print()

    if current_db:
        current_cumulative = current_db['cumulative_usage']
        current_total = (
            current_cumulative['input_tokens'] +
            current_cumulative['output_tokens'] +
            current_cumulative['cache_creation_tokens']
        )

        print("📊 Current Database:")
        print(f"   Total Sessions: {current_cumulative['total_sessions']:,}")
        print(f"   TOTAL PROCESSED: {current_total:,} tokens")
        print()

        diff = total_processed - current_total
        print(f"⚠️  DIFFERENCE: {diff:,} tokens ({diff/1_000_000:.2f}M)")
        print()

    # Create new database with historical peak as starting point
    new_db = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "period_start": "2025-10-01",
        "restored_from_peak": HISTORICAL_PEAK['date'],
        "cumulative_usage": {
            "input_tokens": HISTORICAL_PEAK['input_tokens'],
            "output_tokens": HISTORICAL_PEAK['output_tokens'],
            "cache_creation_tokens": HISTORICAL_PEAK['cache_creation_tokens'],
            "cache_read_tokens": HISTORICAL_PEAK['cache_read_tokens'],
            "total_sessions": HISTORICAL_PEAK['total_sessions']
        },
        "processed_sessions": {},  # Will be rebuilt on next run
        "run_history": [
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "action": "restored_from_historical_peak",
                "peak_date": HISTORICAL_PEAK['date'],
                "peak_tokens": total_processed
            }
        ]
    }

    # Save restored database
    with open(CUMULATIVE_DB, 'w', encoding='utf-8') as f:
        json.dump(new_db, f, indent=2, ensure_ascii=False)

    print("✅ Database restored to historical peak!")
    print()
    print("=" * 70)
    print("🎯 NEXT STEPS")
    print("=" * 70)
    print()
    print("1. Run ccusage to scan for NEW sessions since Nov 21:")
    print("   ccusage")
    print()
    print("2. This will ADD new sessions to the restored peak count")
    print()
    print("3. Your count will now be CUMULATIVE from the peak forward!")
    print()
    print("=" * 70)

def main():
    """Main execution"""
    print()
    restore_from_peak()
    print()

if __name__ == "__main__":
    main()
