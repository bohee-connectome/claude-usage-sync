#!/usr/bin/env python3
"""
Debug version of calculate_usage.py to identify why session count decreased
"""

import sys
import io
import json
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict

# Set UTF-8 encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Find all jsonl files
project_dir = Path.home() / ".claude" / "projects"
jsonl_files = list(project_dir.glob("**/*.jsonl"))

print(f"Total JSONL files found: {len(jsonl_files)}\n")

# Counters
total_input_tokens = 0
total_output_tokens = 0
total_cache_creation_tokens = 0
total_cache_read_tokens = 0
sessions_in_period = 0
sessions_before_cutoff = 0
lines_processed = 0
lines_with_errors = 0
files_with_errors = []

cutoff_date = datetime(2025, 10, 1, tzinfo=timezone.utc)

print(f"Cutoff date: {cutoff_date}")
print("=" * 70)

# Process each file
for idx, jsonl_file in enumerate(jsonl_files):
    file_sessions = 0
    file_sessions_before = 0

    try:
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if not line.strip():
                    continue

                lines_processed += 1

                try:
                    data = json.loads(line)

                    # Check timestamp
                    if 'timestamp' in data:
                        timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))

                        # Count sessions before cutoff
                        if timestamp < cutoff_date:
                            sessions_before_cutoff += 1
                            file_sessions_before += 1
                            continue

                    # Extract usage if it exists
                    if 'message' in data and 'usage' in data['message']:
                        usage = data['message']['usage']

                        total_input_tokens += usage.get('input_tokens', 0)
                        total_output_tokens += usage.get('output_tokens', 0)
                        total_cache_creation_tokens += usage.get('cache_creation_input_tokens', 0)
                        total_cache_read_tokens += usage.get('cache_read_input_tokens', 0)

                        sessions_in_period += 1
                        file_sessions += 1

                except json.JSONDecodeError as e:
                    lines_with_errors += 1
                    continue

    except Exception as e:
        print(f"ERROR processing {jsonl_file.name}: {e}")
        files_with_errors.append(jsonl_file.name)
        continue

    # Print file stats if it has data
    if file_sessions > 0 or file_sessions_before > 0:
        print(f"{idx+1:3}. {jsonl_file.name[:50]:50} | After: {file_sessions:4} | Before: {file_sessions_before:4}")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"Total lines processed:        {lines_processed:,}")
print(f"Lines with JSON errors:       {lines_with_errors:,}")
print(f"Sessions BEFORE Oct 1, 2025:  {sessions_before_cutoff:,}")
print(f"Sessions AFTER Oct 1, 2025:   {sessions_in_period:,}")
print(f"\nTotal sessions counted:       {sessions_in_period:,}")
print()
print("TOKEN TOTALS:")
print(f"  Input:          {total_input_tokens:,}")
print(f"  Output:         {total_output_tokens:,}")
print(f"  Cache Creation: {total_cache_creation_tokens:,}")
print(f"  Cache Read:     {total_cache_read_tokens:,}")

if files_with_errors:
    print(f"\nFiles with errors: {len(files_with_errors)}")
    for f in files_with_errors:
        print(f"  - {f}")

# Calculate cost
input_cost = (total_input_tokens / 1_000_000) * 3.0
output_cost = (total_output_tokens / 1_000_000) * 15.0
cache_write_cost = (total_cache_creation_tokens / 1_000_000) * 3.75
cache_read_cost = (total_cache_read_tokens / 1_000_000) * 0.30
total_cost = input_cost + output_cost + cache_write_cost + cache_read_cost

print(f"\nEstimated total cost: ${total_cost:.2f}")
print("=" * 70)
