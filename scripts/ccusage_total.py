#!/usr/bin/env python3
"""
Show combined Claude usage from all devices

Created & Directed by Bohee Lee
https://github.com/bohee-connectome

Built with Claude Code
"""

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime

CONFIG_FILE = Path.home() / ".claude" / "usage_sync_config.json"

def load_config():
    """Load sync configuration"""
    if not CONFIG_FILE.exists():
        print("❌ Not configured yet")
        print()
        print("Run setup first:")
        print("  ccusage-sync")
        sys.exit(1)

    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def pull_latest(repo_path):
    """Pull latest data from Git"""
    print("🔄 Pulling latest data...")
    result = subprocess.run(
        ['git', 'pull'],
        cwd=repo_path,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print("⚠️  Pull failed (continuing with local data)")
        print(result.stderr)
    else:
        print("✅ Data synced")

    print()

def aggregate_usage(data_dir):
    """Aggregate usage from all device JSON files"""
    data_dir = Path(data_dir)

    if not data_dir.exists():
        print(f"❌ Data directory not found: {data_dir}")
        sys.exit(1)

    json_files = list(data_dir.glob("*.json"))

    if not json_files:
        print("❌ No usage data found")
        print()
        print("Make sure to run 'ccusage-sync' on each device first")
        sys.exit(1)

    # Aggregate data
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

            device_info = {
                'device_id': data.get('device_id', json_file.stem),
                'last_updated': data.get('last_updated'),
                'cost': data.get('estimated_cost', 0)
            }

            usage = data.get('usage', {})

            # Add to totals
            total_usage['input_tokens'] += usage.get('input_tokens', 0)
            total_usage['output_tokens'] += usage.get('output_tokens', 0)
            total_usage['cache_creation_tokens'] += usage.get('cache_creation_tokens', 0)
            total_usage['cache_read_tokens'] += usage.get('cache_read_tokens', 0)
            total_usage['total_sessions'] += usage.get('total_sessions', 0)

            # Store device info
            device_info['usage'] = usage
            devices.append(device_info)

        except Exception as e:
            print(f"⚠️  Error reading {json_file.name}: {e}")
            continue

    return total_usage, devices

def display_results(total_usage, devices):
    """Display formatted results"""
    print("=" * 70)
    print("CLAUDE TOTAL USAGE (All Devices)")
    print(f"Period: October 1, 2025 - {datetime.now().strftime('%B %d, %Y')}")
    print("=" * 70)
    print()

    print(f"💻 Total Devices:      {len(devices)}")
    print(f"📊 Total Sessions:     {total_usage['total_sessions']:,}")
    print()

    print("🔢 COMBINED TOKEN USAGE:")
    print(f"  Input Tokens:        {total_usage['input_tokens']:,}")
    print(f"  Output Tokens:       {total_usage['output_tokens']:,}")
    print(f"  Cache Creation:      {total_usage['cache_creation_tokens']:,}")
    print(f"  Cache Read:          {total_usage['cache_read_tokens']:,}")
    print()

    total_processed = (
        total_usage['input_tokens'] +
        total_usage['output_tokens'] +
        total_usage['cache_creation_tokens']
    )
    print(f"💾 TOTAL PROCESSED:    {total_processed:,}")
    print()

    # Calculate total cost
    input_cost = (total_usage['input_tokens'] / 1_000_000) * 3.0
    output_cost = (total_usage['output_tokens'] / 1_000_000) * 15.0
    cache_w = (total_usage['cache_creation_tokens'] / 1_000_000) * 3.75
    cache_r = (total_usage['cache_read_tokens'] / 1_000_000) * 0.30
    total_cost = input_cost + output_cost + cache_w + cache_r

    print("💵 TOTAL ESTIMATED COST (Sonnet 4.5):")
    print(f"  Input:       ${input_cost:.2f}")
    print(f"  Output:      ${output_cost:.2f}")
    print(f"  Cache Write: ${cache_w:.2f}")
    print(f"  Cache Read:  ${cache_r:.2f}")
    print()
    print(f"  TOTAL:       ${total_cost:.2f}")

    print()
    print("=" * 70)
    print("📱 BREAKDOWN BY DEVICE:")
    print("=" * 70)
    print()

    # Sort devices by cost
    devices_sorted = sorted(devices, key=lambda d: d['cost'], reverse=True)

    for device in devices_sorted:
        usage = device['usage']
        device_total = (
            usage.get('input_tokens', 0) +
            usage.get('output_tokens', 0) +
            usage.get('cache_creation_tokens', 0)
        )

        last_updated = device.get('last_updated', 'Unknown')
        if last_updated != 'Unknown':
            try:
                dt = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
                last_updated = dt.strftime('%Y-%m-%d %H:%M')
            except:
                pass

        print(f"🖥️  {device['device_id']}")
        print(f"   Tokens:  {device_total:,}")
        print(f"   Cost:    ${device['cost']:.2f}")
        print(f"   Updated: {last_updated}")
        print()

    print("=" * 70)

def main():
    """Main execution"""
    print("🚀 Claude Total Usage Calculator")
    print()

    # Load config
    config = load_config()

    repo_path = Path(config['repo_path'])
    data_dir = Path(config['data_dir'])

    # Pull latest data
    pull_latest(repo_path)

    # Aggregate usage
    total_usage, devices = aggregate_usage(data_dir)

    # Display results
    display_results(total_usage, devices)

if __name__ == "__main__":
    main()
