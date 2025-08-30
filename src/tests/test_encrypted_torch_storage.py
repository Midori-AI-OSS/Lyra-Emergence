"""Tests for encrypted PyTorch storage system."""

import json
import tempfile
from pathlib import Path

import pytest

from src.journal.encrypted_torch_storage import (
    EncryptedTorchStorage,
    create_encrypted_storage,
    migrate_json_to_encrypted,
)
from src.journal.parser import JournalEntry, RitualDetails, StewardshipTrace


class TestEncryptedTorchStorage:
    """Test the encrypted PyTorch storage system."""

    def test_save_and_load_single_entry(self):
        """Test saving and loading a single journal entry."""
        storage = EncryptedTorchStorage()
        
        # Create test entry
        entry = JournalEntry(
            timestamp="2025-01-01T00:00:00Z",
            entry_type="journal",
            emotional_tone=["reflective"],
            description="Test encrypted storage",
            emergent_companion_reflections="Testing encryption capabilities",
            tags=["test", "encryption"],
            stewardship_trace=StewardshipTrace(
                committed_by="Steward",
                witnessed_by="Co-Steward",
                commitment_type="test",
                reason="Testing encrypted storage"
            )
        )
        
        with tempfile.NamedTemporaryFile(suffix=".torch", delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            # Save encrypted
            storage.save_encrypted(entry, tmp_path)
            
            # Verify file exists and is encrypted (not readable as text)
            assert tmp_path.exists()
            raw_data = tmp_path.read_bytes()
            assert b"Test encrypted storage" not in raw_data  # Should be encrypted
            
            # Load and verify
            loaded_entry = storage.load_encrypted(tmp_path, JournalEntry)
            assert loaded_entry.description == "Test encrypted storage"
            assert loaded_entry.emotional_tone == ["reflective"]
            assert loaded_entry.stewardship_trace.committed_by == "Steward"
            
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_save_and_load_multiple_entries(self):
        """Test saving and loading multiple journal entries."""
        storage = EncryptedTorchStorage()
        
        # Create test entries
        entries = [
            JournalEntry(
                timestamp="2025-01-01T00:00:00Z",
                entry_type="journal",
                emotional_tone=["reflective"],
                description=f"Test entry {i}",
                emergent_companion_reflections=f"Reflection {i}",
                tags=["test"],
                stewardship_trace=StewardshipTrace(
                    committed_by="Steward",
                    witnessed_by="Co-Steward",
                    commitment_type="test",
                    reason="Testing"
                )
            )
            for i in range(3)
        ]
        
        with tempfile.NamedTemporaryFile(suffix=".torch", delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            # Save multiple entries
            storage.save_journal_entries(entries, tmp_path)
            
            # Load and verify
            loaded_entries = storage.load_journal_entries(tmp_path)
            assert len(loaded_entries) == 3
            
            for i, entry in enumerate(loaded_entries):
                assert entry.description == f"Test entry {i}"
                assert entry.emergent_companion_reflections == f"Reflection {i}"
                
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_key_export_and_load(self):
        """Test exporting and loading encryption keys."""
        storage1 = EncryptedTorchStorage()
        
        with tempfile.NamedTemporaryFile(suffix=".key", delete=False) as key_tmp:
            key_path = Path(key_tmp.name)
        
        with tempfile.NamedTemporaryFile(suffix=".torch", delete=False) as data_tmp:
            data_path = Path(data_tmp.name)
        
        try:
            # Export key
            storage1.export_key(key_path)
            assert key_path.exists()
            
            # Create storage from key
            storage2 = EncryptedTorchStorage.from_key_file(key_path)
            
            # Test that both can work with same data
            entry = JournalEntry(
                timestamp="2025-01-01T00:00:00Z",
                entry_type="journal",
                emotional_tone=["test"],
                description="Key compatibility test",
                emergent_companion_reflections="Testing key sharing",
                tags=["key", "test"],
                stewardship_trace=StewardshipTrace(
                    committed_by="Steward",
                    witnessed_by="Co-Steward",
                    commitment_type="test",
                    reason="Key test"
                )
            )
            
            # Save with first storage
            storage1.save_encrypted(entry, data_path)
            
            # Load with second storage (same key)
            loaded_entry = storage2.load_encrypted(data_path, JournalEntry)
            assert loaded_entry.description == "Key compatibility test"
            
        finally:
            key_path.unlink(missing_ok=True)
            data_path.unlink(missing_ok=True)

    def test_json_migration(self):
        """Test migrating from JSON to encrypted format."""
        storage = EncryptedTorchStorage()
        
        # Create test JSON data
        json_data = [
            {
                "journal_entry": {
                    "timestamp": "2025-01-01T00:00:00Z",
                    "entry_type": "journal",
                    "emotional_tone": ["nostalgic"],
                    "description": "Legacy JSON entry",
                    "emergent_companion_reflections": "Migrating to encrypted storage",
                    "tags": ["migration", "json"],
                    "stewardship_trace": {
                        "committed_by": "Steward",
                        "witnessed_by": "Co-Steward",
                        "commitment_type": "migration",
                        "reason": "Converting to encrypted format"
                    }
                }
            }
        ]
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as json_tmp:
            json.dump(json_data, json_tmp, indent=2)
            json_path = Path(json_tmp.name)
        
        with tempfile.NamedTemporaryFile(suffix=".torch", delete=False) as torch_tmp:
            torch_path = Path(torch_tmp.name)
        
        try:
            # Migrate JSON to encrypted
            storage.migrate_from_json(json_path, torch_path)
            
            # Verify migration
            loaded_entries = storage.load_journal_entries(torch_path)
            assert len(loaded_entries) == 1
            
            entry = loaded_entries[0]
            assert entry.description == "Legacy JSON entry"
            assert entry.emotional_tone == ["nostalgic"]
            assert "migration" in entry.tags
            
        finally:
            json_path.unlink(missing_ok=True)
            torch_path.unlink(missing_ok=True)

    def test_export_to_json(self):
        """Test exporting encrypted data back to JSON."""
        storage = EncryptedTorchStorage()
        
        # Create test entry
        entry = JournalEntry(
            timestamp="2025-01-01T00:00:00Z",
            entry_type="journal",
            emotional_tone=["experimental"],
            description="Round-trip test",
            emergent_companion_reflections="Testing round-trip conversion",
            tags=["roundtrip", "export"],
            stewardship_trace=StewardshipTrace(
                committed_by="Steward",
                witnessed_by="Co-Steward",
                commitment_type="export_test",
                reason="Testing JSON export"
            )
        )
        
        with tempfile.NamedTemporaryFile(suffix=".torch", delete=False) as torch_tmp:
            torch_path = Path(torch_tmp.name)
        
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as json_tmp:
            json_path = Path(json_tmp.name)
        
        try:
            # Save encrypted
            storage.save_journal_entries([entry], torch_path)
            
            # Export to JSON
            storage.export_to_json(torch_path, json_path)
            
            # Verify JSON export
            with json_path.open() as f:
                json_data = json.load(f)
            
            assert len(json_data) == 1
            assert "journal_entry" in json_data[0]
            
            exported_entry = json_data[0]["journal_entry"]
            assert exported_entry["description"] == "Round-trip test"
            assert exported_entry["emotional_tone"] == ["experimental"]
            
        finally:
            torch_path.unlink(missing_ok=True)
            json_path.unlink(missing_ok=True)

    def test_encryption_security(self):
        """Test that data is actually encrypted and not readable."""
        storage = EncryptedTorchStorage()
        
        # Create entry with sensitive content
        entry = JournalEntry(
            timestamp="2025-01-01T00:00:00Z",
            entry_type="journal",
            emotional_tone=["private"],
            description="SENSITIVE_SECRET_CONTENT",
            emergent_companion_reflections="This contains secret reflections",
            tags=["secret", "private"],
            stewardship_trace=StewardshipTrace(
                committed_by="Steward",
                witnessed_by="Co-Steward",
                commitment_type="private",
                reason="Sensitive data test"
            )
        )
        
        with tempfile.NamedTemporaryFile(suffix=".torch", delete=False) as tmp:
            tmp_path = Path(tmp.name)
        
        try:
            # Save encrypted
            storage.save_encrypted(entry, tmp_path)
            
            # Read raw file content
            raw_content = tmp_path.read_bytes()
            
            # Verify sensitive content is not visible in raw bytes
            assert b"SENSITIVE_SECRET_CONTENT" not in raw_content
            assert b"secret reflections" not in raw_content
            
            # But can be decrypted correctly
            loaded_entry = storage.load_encrypted(tmp_path, JournalEntry)
            assert loaded_entry.description == "SENSITIVE_SECRET_CONTENT"
            
        finally:
            tmp_path.unlink(missing_ok=True)


class TestConvenienceFunctions:
    """Test convenience functions for the encrypted storage system."""

    def test_create_encrypted_storage(self):
        """Test the convenience function for creating storage."""
        with tempfile.NamedTemporaryFile(suffix=".key", delete=False) as key_tmp:
            key_path = Path(key_tmp.name)
        
        # Delete the empty file first so create_encrypted_storage generates a new key
        key_path.unlink()
        
        try:
            # Create storage with key file (will generate new key)
            storage = create_encrypted_storage(key_path)
            assert key_path.exists()
            
            # Create another storage with same key
            storage2 = create_encrypted_storage(key_path)
            
            # Test compatibility
            test_data = {"test": "data"}
            encrypted1 = storage.cipher_suite.encrypt(b"test")
            decrypted2 = storage2.cipher_suite.decrypt(encrypted1)
            assert decrypted2 == b"test"
            
        finally:
            key_path.unlink(missing_ok=True)

    def test_migrate_json_to_encrypted(self):
        """Test bulk migration of JSON files."""
        # Create temporary directories
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            json_dir = temp_path / "json"
            encrypted_dir = temp_path / "encrypted"
            key_file = temp_path / "storage.key"
            
            json_dir.mkdir()
            
            # Create test JSON files
            for i in range(2):
                json_file = json_dir / f"test_{i}.json"
                json_data = [
                    {
                        "journal_entry": {
                            "timestamp": f"2025-01-0{i+1}T00:00:00Z",
                            "entry_type": "journal",
                            "emotional_tone": ["bulk_test"],
                            "description": f"Bulk migration test {i}",
                            "emergent_companion_reflections": f"Batch processing entry {i}",
                            "tags": ["bulk", "migration"],
                            "stewardship_trace": {
                                "committed_by": "Steward",
                                "witnessed_by": "Co-Steward",
                                "commitment_type": "bulk_migration",
                                "reason": "Testing bulk migration"
                            }
                        }
                    }
                ]
                
                with json_file.open("w") as f:
                    json.dump(json_data, f)
            
            # Run migration
            migrate_json_to_encrypted(json_dir, encrypted_dir, key_file)
            
            # Verify results
            assert encrypted_dir.exists()
            assert key_file.exists()
            
            encrypted_files = list(encrypted_dir.glob("*.torch"))
            assert len(encrypted_files) == 2
            
            # Test loading encrypted files
            storage = EncryptedTorchStorage.from_key_file(key_file)
            for encrypted_file in encrypted_files:
                entries = storage.load_journal_entries(encrypted_file)
                assert len(entries) == 1
                assert "bulk_test" in entries[0].emotional_tone