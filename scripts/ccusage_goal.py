#!/usr/bin/env python3
"""
Check progress toward 100M token goal by December 31, 2025
Uses multi-device total (all devices combined)

Created & Directed by Bohee Lee
https://github.com/bohee-connectome

Built with Claude Code
"""

import sys
import io
import json
from datetime import datetime, timezone
from pathlib import Path

# Set UTF-8 encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Paths
CONFIG_FILE = Path.home() / ".claude" / "usage_sync_config.json"
GOAL_TOKENS = 100_000_000  # 100M tokens
DEADLINE = datetime(2025, 12, 31, 23, 59, 59, tzinfo=timezone.utc)

def load_config():
    """Load sync configuration"""
    if not CONFIG_FILE.exists():
        print("❌ Configuration not found!")
        print()
        print("Run setup first:")
        print("  ccusage-sync")
        sys.exit(1)

    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def load_all_devices():
    """Load usage data from all devices"""
    config = load_config()
    data_dir = Path(config['data_dir'])

    if not data_dir.exists():
        print(f"❌ Data directory not found: {data_dir}")
        sys.exit(1)

    json_files = list(data_dir.glob("*.json"))

    if not json_files:
        print("❌ No usage data found")
        print()
        print("Make sure to run 'ccusage-auto-sync' first")
        sys.exit(1)

    # Aggregate data from all devices
    total_usage = {
        'input_tokens': 0,
        'output_tokens': 0,
        'cache_creation_tokens': 0,
        'cache_read_tokens': 0,
        'total_sessions': 0
    }

    devices = []

    for json_file in json_files:
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)

            usage = data.get('usage', {})

            total_usage['input_tokens'] += usage.get('input_tokens', 0)
            total_usage['output_tokens'] += usage.get('output_tokens', 0)
            total_usage['cache_creation_tokens'] += usage.get('cache_creation_tokens', 0)
            total_usage['cache_read_tokens'] += usage.get('cache_read_tokens', 0)
            total_usage['total_sessions'] += usage.get('total_sessions', 0)

            devices.append({
                'device_id': data.get('device_id', json_file.stem),
                'last_updated': data.get('last_updated')
            })

        except Exception as e:
            print(f"⚠️  Error reading {json_file.name}: {e}")
            continue

    return total_usage, devices

def calculate_progress(cumulative):
    """Calculate progress toward goal"""
    total_processed = (
        cumulative["input_tokens"] +
        cumulative["output_tokens"] +
        cumulative["cache_creation_tokens"]
    )

    remaining = GOAL_TOKENS - total_processed
    progress_pct = (total_processed / GOAL_TOKENS) * 100

    # Calculate days remaining
    now = datetime.now(timezone.utc)
    days_remaining = (DEADLINE - now).days

    # Calculate daily average needed
    if days_remaining > 0:
        daily_needed = remaining / days_remaining
    else:
        daily_needed = 0

    return {
        "total_processed": total_processed,
        "remaining": remaining,
        "progress_pct": progress_pct,
        "days_remaining": days_remaining,
        "daily_needed": daily_needed
    }

def display_goal_progress(cumulative, devices, progress):
    """Display goal progress"""
    print()
    print("=" * 70)
    print("🎯 100M TOKEN GOAL - PROGRESS TRACKER")
    print(f"Deadline: December 31, 2025")
    print("=" * 70)
    print()

    # Current status
    print(f"📊 CURRENT STATUS (All Devices):")
    print(f"   Total Devices:      {len(devices)}")
    print(f"   Total Sessions:     {cumulative['total_sessions']:,}")
    print(f"   Input Tokens:       {cumulative['input_tokens']:,}")
    print(f"   Output Tokens:      {cumulative['output_tokens']:,}")
    print(f"   Cache Creation:     {cumulative['cache_creation_tokens']:,}")
    print()
    print(f"   💰 TOTAL PROCESSED:  {progress['total_processed']:,} tokens")
    print(f"                        ({progress['total_processed']/1_000_000:.2f}M)")
    print()

    # Progress bar
    bar_length = 50
    filled_length = int(bar_length * progress['progress_pct'] / 100)
    bar = '█' * filled_length + '░' * (bar_length - filled_length)

    print(f"🎯 GOAL PROGRESS:")
    print(f"   [{bar}] {progress['progress_pct']:.1f}%")
    print()
    print(f"   Target:    {GOAL_TOKENS:,} tokens (100M)")
    print(f"   Current:   {progress['total_processed']:,} tokens ({progress['total_processed']/1_000_000:.2f}M)")
    print(f"   Remaining: {progress['remaining']:,} tokens ({progress['remaining']/1_000_000:.2f}M)")
    print()

    # Time-based projections
    print(f"⏰ TIME REMAINING:")
    print(f"   Days until deadline: {progress['days_remaining']}")
    print()

    if progress['days_remaining'] > 0:
        print(f"📈 DAILY TARGET:")
        print(f"   Tokens needed per day: {progress['daily_needed']:,.0f} ({progress['daily_needed']/1_000_000:.2f}M)")
        print()

        # Calculate if we're on track
        # Estimate current daily average
        period_start = datetime(2025, 10, 1, tzinfo=timezone.utc)
        days_elapsed = (datetime.now(timezone.utc) - period_start).days
        if days_elapsed > 0:
            current_daily_avg = progress['total_processed'] / days_elapsed
            print(f"📊 CURRENT PACE:")
            print(f"   Current daily average: {current_daily_avg:,.0f} ({current_daily_avg/1_000_000:.2f}M)")
            print()

            # Projection
            total_days = (DEADLINE - period_start).days
            projected_total = current_daily_avg * total_days

            print(f"🔮 PROJECTION (at current pace):")
            print(f"   Projected total by Dec 31: {projected_total:,.0f} ({projected_total/1_000_000:.2f}M)")

            if projected_total >= GOAL_TOKENS:
                surplus = projected_total - GOAL_TOKENS
                print(f"   ✅ ON TRACK! (+{surplus:,.0f} tokens, +{surplus/1_000_000:.2f}M)")
            else:
                deficit = GOAL_TOKENS - projected_total
                print(f"   ⚠️  BEHIND PACE (-{deficit:,.0f} tokens, -{deficit/1_000_000:.2f}M)")
                print(f"   Need to increase daily usage by {(progress['daily_needed'] - current_daily_avg):,.0f} tokens")

    else:
        print("⚠️  DEADLINE HAS PASSED!")

        if progress['remaining'] <= 0:
            print(f"   🎉 GOAL ACHIEVED!")
        else:
            print(f"   ❌ Goal not met (short by {progress['remaining']:,} tokens)")

    print()
    print("=" * 70)

def main():
    """Main execution"""
    cumulative, devices = load_all_devices()
    progress = calculate_progress(cumulative)
    display_goal_progress(cumulative, devices, progress)

if __name__ == "__main__":
    main()
