#!/usr/bin/env python3
"""
Calculate total Claude usage from October 2025 to present
"""

import json
import glob
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# Find all jsonl files
project_dir = Path.home() / ".claude" / "projects"
jsonl_files = list(project_dir.glob("**/*.jsonl"))

print(f"Found {len(jsonl_files)} session files\n")

# Counters
total_input_tokens = 0
total_output_tokens = 0
total_cache_creation_tokens = 0
total_cache_read_tokens = 0

sessions_in_period = 0
# Make cutoff_date timezone-aware (UTC)
from datetime import timezone
cutoff_date = datetime(2025, 10, 1, tzinfo=timezone.utc)

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
                        timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))

                        # Only count from October 1, 2025 onwards
                        if timestamp < cutoff_date:
                            continue

                    # Extract usage if it exists
                    if 'message' in data and 'usage' in data['message']:
                        usage = data['message']['usage']

                        total_input_tokens += usage.get('input_tokens', 0)
                        total_output_tokens += usage.get('output_tokens', 0)
                        total_cache_creation_tokens += usage.get('cache_creation_input_tokens', 0)
                        total_cache_read_tokens += usage.get('cache_read_input_tokens', 0)

                        sessions_in_period += 1

                except json.JSONDecodeError:
                    continue

    except Exception as e:
        print(f"Error processing {jsonl_file}: {e}")
        continue

# Calculate totals
total_tokens = total_input_tokens + total_output_tokens + total_cache_creation_tokens

print("=" * 60)
print("CLAUDE USAGE STATISTICS")
print(f"Period: October 1, 2025 - Present")
print("=" * 60)
print()
print(f"📊 Total Sessions: {sessions_in_period:,}")
print()
print("🔢 TOKEN BREAKDOWN:")
print(f"  Input Tokens:          {total_input_tokens:,}")
print(f"  Output Tokens:         {total_output_tokens:,}")
print(f"  Cache Creation Tokens: {total_cache_creation_tokens:,}")
print(f"  Cache Read Tokens:     {total_cache_read_tokens:,}")
print()
print(f"💰 TOTAL TOKENS:         {total_tokens:,}")
print()
print("=" * 60)

# Estimate costs (approximate pricing for Claude Sonnet 4.5)
# Input: $3/MTok, Output: $15/MTok, Cache Write: $3.75/MTok, Cache Read: $0.30/MTok
input_cost = (total_input_tokens / 1_000_000) * 3.0
output_cost = (total_output_tokens / 1_000_000) * 15.0
cache_write_cost = (total_cache_creation_tokens / 1_000_000) * 3.75
cache_read_cost = (total_cache_read_tokens / 1_000_000) * 0.30

total_cost = input_cost + output_cost + cache_write_cost + cache_read_cost

print("💵 ESTIMATED COST (Sonnet 4.5):")
print(f"  Input:        ${input_cost:.2f}")
print(f"  Output:       ${output_cost:.2f}")
print(f"  Cache Write:  ${cache_write_cost:.2f}")
print(f"  Cache Read:   ${cache_read_cost:.2f}")
print()
print(f"  TOTAL:        ${total_cost:.2f}")
print("=" * 60)
