#!/usr/bin/env python3
"""
Comprehensive JSON Validation Script for Lyra-Emergence Project

This script provides thorough validation of all JSON files in the specified directory recursively.
It checks for:
- Valid JSON syntax
- Proper formatting and encoding
- Schema compliance (where schemas exist)
- Structural integrity
- Security considerations
- Best practices adherence

Usage: python validate_json.py [directory_path]
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


class ComprehensiveJSONValidator:
    """Enhanced JSON validation utility for the Lyra-Emergence project."""

    def __init__(self, directory: str):
        """Initialize validator with target directory."""
        self.directory = Path(directory)
        self.errors: List[Tuple[str, str]] = []
        self.warnings: List[Tuple[str, str]] = []
        self.valid_files: List[str] = []
        self.schemas_dir = self.directory / "Schemas"
        self.schemas: Dict[str, Dict[str, Any]] = {}
        
        # Load schemas if available
        self._load_schemas()

    def _load_schemas(self) -> None:
        """Load all available JSON schemas for validation."""
        if not self.schemas_dir.exists():
            print(f"Note: Schemas directory not found at {self.schemas_dir}")
            return
            
        schema_files = list(self.schemas_dir.glob("*.schema.json"))
        print(f"Loading {len(schema_files)} schemas...")
        
        for schema_file in schema_files:
            try:
                with open(schema_file, 'r', encoding='utf-8') as f:
                    schema = json.load(f)
                    schema_name = schema_file.stem.replace('.schema', '')
                    self.schemas[schema_name] = schema
                    print(f"  ✓ Loaded schema: {schema_name}")
            except Exception as e:
                print(f"  ✗ Failed to load schema {schema_file}: {e}")

    def _find_applicable_schema(self, file_path: Path, data: Dict[str, Any]) -> Dict[str, Any] | None:
        """Find the most applicable schema for a JSON file."""
        file_name = file_path.stem.lower()
        
        # Direct name matching patterns
        schema_patterns = {
            "journal": "journal_entry",
            "manifest": "manifest", 
            "ritual": "rituals",
            "continuity": "continuity_index",
            "behavioral": "behavioral_directives",
            "memory": "memory_protocol",
            "trace": "echo_trace",
            "lexicon": "symbolic_lexicon",
        }
        
        for pattern, schema_name in schema_patterns.items():
            if pattern in file_name and schema_name in self.schemas:
                return self.schemas[schema_name]
                
        # Content-based matching
        if "entries" in data and isinstance(data["entries"], list):
            return self.schemas.get("journal_entry")
        elif "rituals" in data or "ritual_name" in data:
            return self.schemas.get("rituals")
        elif "manifest" in data or "version" in data:
            return self.schemas.get("manifest")
            
        return None

    def _validate_schema_compliance(self, data: Dict[str, Any], schema: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate JSON data against a schema (basic validation)."""
        try:
            # Basic schema validation without external dependencies
            if "$schema" in schema and "properties" in schema:
                required = schema.get("required", [])
                properties = schema.get("properties", {})
                
                # Check required fields
                for field in required:
                    if field not in data:
                        return False, f"Missing required field: {field}"
                
                # Check field types (basic)
                for field, value in data.items():
                    if field in properties:
                        expected_type = properties[field].get("type")
                        if expected_type == "string" and not isinstance(value, str):
                            return False, f"Field '{field}' should be string, got {type(value).__name__}"
                        elif expected_type == "number" and not isinstance(value, (int, float)):
                            return False, f"Field '{field}' should be number, got {type(value).__name__}"
                        elif expected_type == "array" and not isinstance(value, list):
                            return False, f"Field '{field}' should be array, got {type(value).__name__}"
                        elif expected_type == "object" and not isinstance(value, dict):
                            return False, f"Field '{field}' should be object, got {type(value).__name__}"
                
                return True, "Schema validation passed"
            else:
                return True, "Basic schema structure validated"
                
        except Exception as e:
            return False, f"Schema validation error: {e}"

    def _check_security_concerns(self, data: Dict[str, Any], file_path: Path) -> List[str]:
        """Check for potential security issues in JSON data."""
        concerns = []
        json_str = json.dumps(data, ensure_ascii=False).lower()
        
        # Sensitive data patterns
        sensitive_patterns = [
            ("password", "Potential password field detected"),
            ("secret", "Potential secret/API key detected"),
            ("token", "Potential authentication token detected"),
            ("private_key", "Potential private key detected"),
            ("api_key", "Potential API key detected"),
        ]
        
        for pattern, message in sensitive_patterns:
            if pattern in json_str:
                concerns.append(f"SECURITY: {message}")
        
        return concerns

    def _check_best_practices(self, data: Dict[str, Any], file_path: Path, content: str) -> List[str]:
        """Check for JSON best practices and common issues."""
        issues = []
        
        # File size check
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        if file_size_mb > 10:
            issues.append(f"Large file size: {file_size_mb:.1f}MB (consider splitting)")
        
        # Encoding check
        if not content.endswith('\n'):
            issues.append("File should end with newline")
        
        # Depth check
        def check_depth(obj, current_depth=0, max_depth=0):
            max_depth = max(max_depth, current_depth)
            if current_depth > 15:
                return max_depth
            if isinstance(obj, dict):
                for value in obj.values():
                    max_depth = check_depth(value, current_depth + 1, max_depth)
            elif isinstance(obj, list):
                for item in obj:
                    max_depth = check_depth(item, current_depth + 1, max_depth)
            return max_depth
        
        max_depth = check_depth(data)
        if max_depth > 15:
            issues.append(f"Deep nesting detected: {max_depth} levels (consider flattening)")
        
        # Empty objects/arrays check
        def has_empty_containers(obj):
            if isinstance(obj, dict):
                if not obj:
                    return True
                return any(has_empty_containers(v) for v in obj.values())
            elif isinstance(obj, list):
                if not obj:
                    return True
                return any(has_empty_containers(item) for item in obj)
            return False
        
        if has_empty_containers(data):
            issues.append("Empty objects or arrays detected")
        
        # Duplicate keys in string content (basic check)
        lines = content.split('\n')
        seen_keys = set()
        for line in lines:
            if ':' in line:
                key_part = line.split(':')[0].strip().strip('"')
                if key_part in seen_keys and key_part and not key_part.startswith('//'):
                    issues.append(f"Potential duplicate key detected: {key_part}")
                seen_keys.add(key_part)
        
        return issues

    def validate_file(self, file_path: Path) -> Tuple[bool, str | None]:
        """
        Comprehensively validate a single JSON file.

        Args:
            file_path: Path to the JSON file

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Parse JSON to validate syntax
            if not content.strip():
                return False, "File is empty"

            data = json.loads(content)
            
            # Find and apply schema validation
            applicable_schema = self._find_applicable_schema(file_path, data)
            if applicable_schema:
                is_schema_valid, schema_message = self._validate_schema_compliance(data, applicable_schema)
                if not is_schema_valid:
                    return False, f"Schema validation failed: {schema_message}"
                else:
                    print(f"    ✓ Schema validation passed for {file_path.name}")
            
            # Security checks
            security_concerns = self._check_security_concerns(data, file_path)
            for concern in security_concerns:
                self.warnings.append((str(file_path), concern))
            
            # Best practices checks
            best_practice_issues = self._check_best_practices(data, file_path, content)
            for issue in best_practice_issues:
                self.warnings.append((str(file_path), f"BEST_PRACTICE: {issue}"))

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
        print("=" * 60)

        for file_path in json_files:
            print(f"Validating: {file_path.relative_to(self.directory)}")
            is_valid, error = self.validate_file(file_path)

            if is_valid:
                self.valid_files.append(str(file_path))
                print(f"  ✓ Valid JSON file")
            else:
                self.errors.append((str(file_path), error))
                print(f"  ✗ {error}")
            print()

        return len(self.errors) == 0

    def print_summary(self):
        """Print comprehensive validation summary."""
        total_files = len(self.valid_files) + len(self.errors)

        print("\n" + "=" * 80)
        print("COMPREHENSIVE JSON VALIDATION SUMMARY")
        print("=" * 80)
        print(f"Total files processed: {total_files}")
        print(f"Valid files: {len(self.valid_files)}")
        print(f"Invalid files: {len(self.errors)}")
        print(f"Warnings issued: {len(self.warnings)}")
        print(f"Schemas loaded: {len(self.schemas)}")

        if self.errors:
            print(f"\n🚨 ERRORS FOUND ({len(self.errors)}):")
            print("-" * 40)
            for file_path, error in self.errors:
                relative_path = Path(file_path).relative_to(self.directory)
                print(f"  ❌ {relative_path}")
                print(f"     {error}")

        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            print("-" * 40)
            for file_path, warning in self.warnings:
                relative_path = Path(file_path).relative_to(self.directory)
                print(f"  ⚠️  {relative_path}")
                print(f"     {warning}")

        print("\n" + "=" * 80)
        
        # Recommendations
        if self.errors or self.warnings:
            print("RECOMMENDATIONS:")
            if self.errors:
                print("  • Fix JSON syntax and schema compliance errors before deployment")
            if any("SECURITY" in w[1] for w in self.warnings):
                print("  • Review security warnings - sensitive data should be encrypted")
            if any("BEST_PRACTICE" in w[1] for w in self.warnings):
                print("  • Consider addressing best practice issues for maintainability")
        else:
            print("🎉 ALL JSON FILES VALIDATED SUCCESSFULLY!")
            
        print("=" * 80)


def main():
    """Main entry point for the script."""
    if len(sys.argv) < 2:
        print("Usage: python validate_json.py [directory_path]")
        print("Example: python validate_json.py data/")
        print("\nThis script performs comprehensive validation of JSON files including:")
        print("  • Syntax validation")
        print("  • Schema compliance (where schemas exist)")
        print("  • Security concern detection")
        print("  • Best practices checking")
        sys.exit(1)

    directory = sys.argv[1]
    validator = ComprehensiveJSONValidator(directory)

    print("🔍 Starting comprehensive JSON validation...")
    print(f"📁 Target directory: {directory}")
    print()
    
    is_valid = validator.validate_directory()
    validator.print_summary()

    if not is_valid:
        print("\n❌ JSON validation failed!")
        sys.exit(1)
    else:
        if validator.warnings:
            print(f"\n✅ All JSON files are syntactically valid! ({len(validator.warnings)} warnings)")
        else:
            print("\n✅ All JSON files are perfect!")
        sys.exit(0)


if __name__ == "__main__":
    main()
