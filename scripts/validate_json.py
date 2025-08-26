#!/usr/bin/env python3
"""
JSON Validation Script for Lyra-Emergence Project

This script validates all JSON files in the specified directory recursively.
It checks for:
- Valid JSON syntax
- Proper formatting
- Structural integrity

Usage: python validate_json.py [directory_path]
"""

import json
import sys
from pathlib import Path


class JSONValidator:
    """JSON validation utility for the Lyra-Emergence project."""

    def __init__(self, directory: str):
        """Initialize validator with target directory."""
        self.directory = Path(directory)
        self.errors: list[tuple[str, str]] = []
        self.valid_files: list[str] = []

    def validate_file(self, file_path: Path) -> tuple[bool, str | None]:
        """
        Validate a single JSON file.

        Args:
            file_path: Path to the JSON file

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Parse JSON to validate syntax
            json.loads(content)

            # Check for common formatting issues
            if not content.strip():
                return False, "File is empty"

            # Validate that file ends with newline (good practice)
            if not content.endswith("\n"):
                print(f"Warning: {file_path} does not end with newline")

            return True, None

        except json.JSONDecodeError as e:
            return False, f"JSON decode error: {e}"
        except UnicodeDecodeError as e:
            return False, f"Unicode decode error: {e}"
        except FileNotFoundError:
            return False, "File not found"
        except PermissionError:
            return False, "Permission denied"
        except Exception as e:
            return False, f"Unexpected error: {e}"

    def validate_directory(self) -> bool:
        """
        Validate all JSON files in the directory recursively.

        Returns:
            True if all files are valid, False otherwise
        """
        if not self.directory.exists():
            print(f"Error: Directory '{self.directory}' does not exist")
            return False

        # Find all JSON files recursively
        json_files = list(self.directory.rglob("*.json"))

        if not json_files:
            print(f"No JSON files found in '{self.directory}'")
            return True

        print(f"Found {len(json_files)} JSON files to validate...")

        for file_path in json_files:
            is_valid, error = self.validate_file(file_path)

            if is_valid:
                self.valid_files.append(str(file_path))
                print(f"✓ {file_path.relative_to(self.directory)}")
            else:
                self.errors.append((str(file_path), error))
                print(f"✗ {file_path.relative_to(self.directory)}: {error}")

        return len(self.errors) == 0

    def print_summary(self):
        """Print validation summary."""
        total_files = len(self.valid_files) + len(self.errors)

        print("\n" + "=" * 60)
        print("JSON Validation Summary")
        print("=" * 60)
        print(f"Total files processed: {total_files}")
        print(f"Valid files: {len(self.valid_files)}")
        print(f"Invalid files: {len(self.errors)}")

        if self.errors:
            print("\nErrors found:")
            for file_path, error in self.errors:
                print(f"  {file_path}: {error}")

        print("=" * 60)


def main():
    """Main entry point for the script."""
    if len(sys.argv) != 2:
        print("Usage: python validate_json.py [directory_path]")
        print("Example: python validate_json.py data/")
        sys.exit(1)

    directory = sys.argv[1]
    validator = JSONValidator(directory)

    is_valid = validator.validate_directory()
    validator.print_summary()

    if not is_valid:
        print("\n❌ JSON validation failed!")
        sys.exit(1)
    else:
        print("\n✅ All JSON files are valid!")
        sys.exit(0)


if __name__ == "__main__":
    main()
