#!/usr/bin/env python3
"""
Automatic cumulative usage sync to Git

This script:
1. Runs cumulative tracker to update counts
2. Backs up cumulative database to Git repo
3. Updates device-specific JSON for multi-device tracking

Run this daily via Windows Task Scheduler

Created & Directed by Bohee Lee
https://github.com/bohee-connectome

Built with Claude Code
"""

import sys
import io
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# Set UTF-8 encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Paths
SCRIPT_DIR = Path(__file__).parent
REPO_DIR = SCRIPT_DIR.parent
CUMULATIVE_DB = Path.home() / ".claude" / "cumulative_usage.json"
DATA_DIR = REPO_DIR / "data"
DEVICE_ID = "yangpyungpc"  # Change this for each device

def run_cumulative_tracker():
    """Run cumulative tracker to update counts"""
    print("=" * 70)
    print("STEP 1: Running cumulative tracker...")
    print("=" * 70)
    print()

    cumulative_script = SCRIPT_DIR / "ccusage_cumulative.py"

    result = subprocess.run(
        [sys.executable, str(cumulative_script)],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )

    print(result.stdout)

    if result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
        return False

    return True

def export_to_device_json():
    """Export cumulative data to device-specific JSON"""
    print()
    print("=" * 70)
    print("STEP 2: Exporting to device JSON...")
    print("=" * 70)
    print()

    # Load cumulative database
    if not CUMULATIVE_DB.exists():
        print("❌ Cumulative database not found!")
        return False

    with open(CUMULATIVE_DB, 'r', encoding='utf-8') as f:
        db = json.load(f)

    cumulative = db["cumulative_usage"]

    # Create device JSON
    device_data = {
        "device_id": DEVICE_ID,
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "period_start": db["period_start"],
        "period_end": datetime.now().strftime("%Y-%m-%d"),
        "usage": {
            "input_tokens": cumulative["input_tokens"],
            "output_tokens": cumulative["output_tokens"],
            "cache_creation_tokens": cumulative["cache_creation_tokens"],
            "cache_read_tokens": cumulative["cache_read_tokens"],
            "total_sessions": cumulative["total_sessions"]
        },
        "estimated_cost": (
            (cumulative["input_tokens"] / 1_000_000) * 3.0 +
            (cumulative["output_tokens"] / 1_000_000) * 15.0 +
            (cumulative["cache_creation_tokens"] / 1_000_000) * 3.75 +
            (cumulative["cache_read_tokens"] / 1_000_000) * 0.30
        )
    }

    # Save to data directory
    DATA_DIR.mkdir(exist_ok=True)
    device_file = DATA_DIR / f"{DEVICE_ID}.json"

    with open(device_file, 'w', encoding='utf-8') as f:
        json.dump(device_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Exported to: {device_file}")
    print(f"   Sessions: {cumulative['total_sessions']:,}")
    print(f"   Cost: ${device_data['estimated_cost']:.2f}")

    return True

def backup_to_git():
    """Backup to Git repository"""
    print()
    print("=" * 70)
    print("STEP 3: Backing up to Git...")
    print("=" * 70)
    print()

    try:
        # Git add
        subprocess.run(
            ['git', 'add', '-A'],
            cwd=REPO_DIR,
            check=True,
            capture_output=True
        )

        # Git commit
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_msg = f"Auto-sync: {DEVICE_ID} at {timestamp}"

        result = subprocess.run(
            ['git', 'commit', '-m', commit_msg],
            cwd=REPO_DIR,
            capture_output=True,
            text=True
        )

        if "nothing to commit" in result.stdout:
            print("✅ No changes to commit (already up to date)")
        else:
            print(f"✅ Committed: {commit_msg}")

        # Git push
        subprocess.run(
            ['git', 'push'],
            cwd=REPO_DIR,
            check=True,
            capture_output=True
        )

        print("✅ Pushed to remote repository")
        print()
        print("🎉 Backup complete!")

        return True

    except subprocess.CalledProcessError as e:
        print(f"⚠️  Git operation failed: {e}")
        print("   (Continuing anyway - local data is safe)")
        return False

def main():
    """Main execution"""
    print()
    print("🔄 AUTOMATIC CUMULATIVE USAGE SYNC")
    print(f"Device: {DEVICE_ID}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Step 1: Run cumulative tracker
    if not run_cumulative_tracker():
        print("❌ Failed at step 1")
        sys.exit(1)

    # Step 2: Export to device JSON
    if not export_to_device_json():
        print("❌ Failed at step 2")
        sys.exit(1)

    # Step 3: Backup to Git
    backup_to_git()

    print()
    print("=" * 70)
    print("✅ ALL STEPS COMPLETED")
    print("=" * 70)

if __name__ == "__main__":
    main()
