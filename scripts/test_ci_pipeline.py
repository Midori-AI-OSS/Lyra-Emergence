#!/usr/bin/env python3
"""
Simple test script to validate the CI/CD pipeline setup locally.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return success status."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print("=" * 60)

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ SUCCESS")
        if result.stdout:
            print(f"Output:\n{result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ FAILED (exit code: {e.returncode})")
        if e.stdout:
            print(f"Stdout:\n{e.stdout}")
        if e.stderr:
            print(f"Stderr:\n{e.stderr}")
        return False


def main():
    """Test the CI/CD pipeline locally."""
    print("🚀 Testing CI/CD Pipeline Components Locally")

    # Change to project root
    project_root = Path(__file__).parent.parent
    project_root = project_root.resolve()
    print(f"Project root: {project_root}")

    tests = [
        (["python", "scripts/validate_json.py", "data/"], "JSON Validation"),
        (["uv", "run", "pytest", "-v"], "Python Tests"),
    ]

    success_count = 0
    for cmd, description in tests:
        if run_command(cmd, description):
            success_count += 1

    print(f"\n{'='*60}")
    print("SUMMARY")
    print("=" * 60)
    print(f"Tests passed: {success_count}/{len(tests)}")

    if success_count == len(tests):
        print("✅ All CI/CD pipeline components are working!")
        return 0
    else:
        print("❌ Some CI/CD pipeline components failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
