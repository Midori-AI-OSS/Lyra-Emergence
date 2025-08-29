"""Encrypted PyTorch-compiled Pydantic journal storage system.

This module provides an encrypted, PyTorch-optimized storage system for journal entries
while maintaining full Pydantic validation and type safety.
"""

import io
import json
import os
from pathlib import Path
from typing import Any, TypeVar

import torch
from cryptography.fernet import Fernet
from pydantic import BaseModel

from .parser import JournalEntry, RitualContribution, RitualDetails, StewardshipTrace

T = TypeVar("T", bound=BaseModel)


class EncryptedTorchStorage:
    """Encrypted PyTorch-based storage system for Pydantic models."""
    
    def __init__(self, encryption_key: bytes | None = None):
        """Initialize the encrypted storage system.
        
        Args:
            encryption_key: Encryption key for data protection. If None, generates a new key.
        """
        if encryption_key is None:
            encryption_key = Fernet.generate_key()
        
        self.cipher_suite = Fernet(encryption_key)
        self.encryption_key = encryption_key
        
        # Compile serialization functions for optimization if available
        if hasattr(torch, 'compile'):
            self._torch_save_compiled = torch.compile(self._torch_save_raw)
            self._torch_load_compiled = torch.compile(self._torch_load_raw)
        else:
            self._torch_save_compiled = self._torch_save_raw
            self._torch_load_compiled = self._torch_load_raw
    
    def _torch_save_raw(self, data: Any) -> bytes:
        """Raw PyTorch save function."""
        buffer = io.BytesIO()
        torch.save(data, buffer)
        return buffer.getvalue()
    
    def _torch_load_raw(self, data_bytes: bytes) -> Any:
        """Raw PyTorch load function."""
        buffer = io.BytesIO(data_bytes)
        return torch.load(buffer, weights_only=False)
    
    def save_encrypted(self, model: BaseModel, filepath: Path) -> None:
        """Save a Pydantic model with encryption and PyTorch optimization.
        
        Args:
            model: Pydantic model to save
            filepath: Path to save the encrypted file
        """
        # Convert Pydantic model to serializable dict
        model_dict = model.model_dump()
        
        # Use compiled PyTorch serialization for optimization
        torch_bytes = self._torch_save_compiled(model_dict)
        
        # Encrypt the serialized data
        encrypted_data = self.cipher_suite.encrypt(torch_bytes)
        
        # Save to file
        filepath.write_bytes(encrypted_data)
    
    def load_encrypted(self, filepath: Path, model_class: type[T]) -> T:
        """Load and decrypt a Pydantic model from encrypted PyTorch data.
        
        Args:
            filepath: Path to the encrypted file
            model_class: Pydantic model class to instantiate
            
        Returns:
            Validated Pydantic model instance
        """
        # Read encrypted data
        encrypted_data = filepath.read_bytes()
        
        # Decrypt the data
        torch_bytes = self.cipher_suite.decrypt(encrypted_data)
        
        # Use compiled PyTorch deserialization
        model_dict = self._torch_load_compiled(torch_bytes)
        
        # Validate and create Pydantic model
        return model_class.model_validate(model_dict)
    
    def save_journal_entries(self, entries: list[JournalEntry], filepath: Path) -> None:
        """Save a list of journal entries with encryption.
        
        Args:
            entries: List of journal entries to save
            filepath: Path to save the encrypted file
        """
        # Convert all entries to dicts for serialization
        entries_data = [entry.model_dump() for entry in entries]
        
        # Use PyTorch serialization with optimization
        torch_bytes = self._torch_save_compiled(entries_data)
        
        # Encrypt and save
        encrypted_data = self.cipher_suite.encrypt(torch_bytes)
        filepath.write_bytes(encrypted_data)
    
    def load_journal_entries(self, filepath: Path) -> list[JournalEntry]:
        """Load and decrypt journal entries from encrypted file.
        
        Args:
            filepath: Path to the encrypted file
            
        Returns:
            List of validated journal entries
        """
        # Read and decrypt
        encrypted_data = filepath.read_bytes()
        torch_bytes = self.cipher_suite.decrypt(encrypted_data)
        
        # Deserialize with PyTorch
        entries_data = self._torch_load_compiled(torch_bytes)
        
        # Validate each entry with Pydantic
        return [JournalEntry.model_validate(entry_data) for entry_data in entries_data]
    
    def export_key(self, key_file: Path) -> None:
        """Export the encryption key to a secure file.
        
        Args:
            key_file: Path to save the encryption key
        """
        key_file.write_bytes(self.encryption_key)
        # Set restrictive permissions (owner read/write only)
        os.chmod(key_file, 0o600)
    
    @classmethod
    def from_key_file(cls, key_file: Path) -> "EncryptedTorchStorage":
        """Create storage instance from an existing key file.
        
        Args:
            key_file: Path to the encryption key file
            
        Returns:
            EncryptedTorchStorage instance with loaded key
        """
        encryption_key = key_file.read_bytes()
        return cls(encryption_key)
    
    def migrate_from_json(self, json_file: Path, encrypted_file: Path) -> None:
        """Migrate existing JSON journal files to encrypted PyTorch format.
        
        Args:
            json_file: Path to existing JSON journal file
            encrypted_file: Path for new encrypted file
        """
        # Load existing entries using the current parser
        from .parser import parse_journal
        
        entries = parse_journal(json_file)
        
        # Save in encrypted format
        self.save_journal_entries(entries, encrypted_file)
    
    def export_to_json(self, encrypted_file: Path, json_file: Path) -> None:
        """Export encrypted journal entries back to JSON format.
        
        Useful for debugging, inspection, or creating backups.
        
        Args:
            encrypted_file: Path to encrypted journal file
            json_file: Path for exported JSON file
        """
        # Load encrypted entries
        entries = self.load_journal_entries(encrypted_file)
        
        # Convert to JSON format with journal_entry wrapper
        json_data = []
        for entry in entries:
            json_data.append({"journal_entry": entry.model_dump()})
        
        # Save as JSON
        with json_file.open("w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)


# Convenience functions for common operations
def create_encrypted_storage(key_file: Path | None = None) -> EncryptedTorchStorage:
    """Create a new encrypted storage system.
    
    Args:
        key_file: Optional path to save/load encryption key
        
    Returns:
        EncryptedTorchStorage instance
    """
    if key_file and key_file.exists():
        return EncryptedTorchStorage.from_key_file(key_file)
    
    storage = EncryptedTorchStorage()
    
    if key_file:
        storage.export_key(key_file)
    
    return storage


def migrate_json_to_encrypted(
    json_dir: Path, 
    encrypted_dir: Path, 
    key_file: Path
) -> None:
    """Migrate all JSON journal files to encrypted format.
    
    Args:
        json_dir: Directory containing JSON journal files
        encrypted_dir: Directory for encrypted files
        key_file: Path for encryption key
    """
    storage = create_encrypted_storage(key_file)
    encrypted_dir.mkdir(exist_ok=True)
    
    for json_file in json_dir.glob("*.json"):
        if (json_file.name.endswith(".backup") or 
            json_file.name.startswith("journal_manifest") or
            json_file.name.startswith("journal_index")):
            continue  # Skip backup and manifest files
            
        encrypted_file = encrypted_dir / f"{json_file.stem}.torch"
        storage.migrate_from_json(json_file, encrypted_file)
        print(f"Migrated {json_file.name} -> {encrypted_file.name}")