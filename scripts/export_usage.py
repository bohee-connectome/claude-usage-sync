#!/usr/bin/env python3
"""
Export local Claude usage to JSON file
"""

import json
import socket
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict

def get_device_id():
    """Get unique device identifier"""
    hostname = socket.gethostname()
    # Clean hostname for filename
    device_id = hostname.replace('.', '-').replace(' ', '-').lower()
    return device_id

def calculate_local_usage():
    """Calculate usage from local .claude directory"""
    project_dir = Path.home() / ".claude" / "projects"

    if not project_dir.exists():
        return None

    jsonl_files = list(project_dir.glob("**/*.jsonl"))

    total_input = 0
    total_output = 0
    total_cache_creation = 0
    total_cache_read = 0
    sessions_count = 0

    cutoff_date = datetime(2025, 10, 1, tzinfo=timezone.utc)

    for jsonl_file in jsonl_files:
        try:
            with open(jsonl_file, 'r') as f:
                for line in f:
                    if not line.strip():
                        continue

                    try:
                        data = json.loads(line)

                        # Check timestamp
                        if 'timestamp' in data:
                            timestamp = datetime.fromisoformat(
                                data['timestamp'].replace('Z', '+00:00')
                            )
                            if timestamp < cutoff_date:
                                continue

                        # Extract usage
                        if 'message' in data and 'usage' in data['message']:
                            usage = data['message']['usage']
                            total_input += usage.get('input_tokens', 0)
                            total_output += usage.get('output_tokens', 0)
                            total_cache_creation += usage.get('cache_creation_input_tokens', 0)
                            total_cache_read += usage.get('cache_read_input_tokens', 0)
                            sessions_count += 1

                    except json.JSONDecodeError:
                        continue

        except Exception:
            continue

    return {
        'input_tokens': total_input,
        'output_tokens': total_output,
        'cache_creation_tokens': total_cache_creation,
        'cache_read_tokens': total_cache_read,
        'total_sessions': sessions_count
    }

def estimate_cost(usage):
    """Estimate cost based on Sonnet 4.5 pricing"""
    input_cost = (usage['input_tokens'] / 1_000_000) * 3.0
    output_cost = (usage['output_tokens'] / 1_000_000) * 15.0
    cache_write_cost = (usage['cache_creation_tokens'] / 1_000_000) * 3.75
    cache_read_cost = (usage['cache_read_tokens'] / 1_000_000) * 0.30

    return round(input_cost + output_cost + cache_write_cost + cache_read_cost, 2)

def export_usage(output_file=None):
    """Export usage to JSON file"""
    device_id = get_device_id()
    usage = calculate_local_usage()

    if not usage:
        print("❌ No usage data found")
        return None

    # Build export data
    export_data = {
        'device_id': device_id,
        'last_updated': datetime.now(timezone.utc).isoformat(),
        'period_start': '2025-10-01',
        'period_end': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
        'usage': usage,
        'estimated_cost': estimate_cost(usage)
    }

    # Default output file
    if not output_file:
        output_file = Path.home() / f"claude-usage-{device_id}.json"
    else:
        output_file = Path(output_file)

    # Write JSON
    with open(output_file, 'w') as f:
        json.dump(export_data, f, indent=2)

    print(f"✅ Usage exported to: {output_file}")
    print()
    print(f"📊 Device: {device_id}")
    print(f"💾 Total tokens: {usage['input_tokens'] + usage['output_tokens'] + usage['cache_creation_tokens']:,}")
    print(f"💵 Estimated cost: ${export_data['estimated_cost']}")

    return output_file

if __name__ == "__main__":
    import sys
    output = sys.argv[1] if len(sys.argv) > 1 else None
    export_usage(output)
