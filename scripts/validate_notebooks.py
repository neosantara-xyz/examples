#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

def validate_notebooks(directory="cookbook"):
    """
    Recursively finds and validates all .ipynb files in the given directory.
    """
    error_count = 0
    file_count = 0
    
    # Path to the directory relative to the project root
    cookbook_path = Path(directory)
    
    if not cookbook_path.exists():
        print(f"Error: Directory '{directory}' not found.")
        sys.exit(1)

    print(f"🔍 Starting JSON validation for all notebooks in '{directory}/'...")
    print("-" * 60)

    for ipynb_file in cookbook_path.rglob("*.ipynb"):
        file_count += 1
        try:
            with open(ipynb_file, "r", encoding="utf-8") as f:
                json.load(f)
            print(f"✅ PASS: {ipynb_file}")
        except json.JSONDecodeError as e:
            error_count += 1
            print(f"❌ FAIL: {ipynb_file}")
            print(f"   Reason: {e}")
        except Exception as e:
            error_count += 1
            print(f"❌ ERROR: Could not read {ipynb_file}")
            print(f"   Reason: {e}")

    print("-" * 60)
    if error_count == 0:
        print(f"🎉 Success! {file_count} notebooks validated. No errors found.")
        return True
    else:
        print(f"⚠️  Found {error_count} errors across {file_count} notebooks.")
        return False

if __name__ == "__main__":
    success = validate_notebooks()
    if not success:
        sys.exit(1)
