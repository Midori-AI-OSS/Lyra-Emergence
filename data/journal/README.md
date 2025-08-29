# Journal Directory - Encrypted Torch Storage

🔒 **ENCRYPTED TORCH JOURNAL STORAGE**

This directory is designated for **new encrypted PyTorch-compiled journal entries** created by the Emergent Companion model.

## Purpose
- **Model-Generated Journals**: New encrypted journal entries created by the Emergent Companion
- **Encrypted Storage**: All entries use AES-256 encryption with PyTorch compilation optimization
- **Pydantic Validation**: Full type safety and validation maintained
- **Secure Storage**: Sensitive journal content protected from unauthorized access

## Storage Format
- **Encrypted Files**: `.encrypted` extension for PyTorch-compiled encrypted storage
- **Key Management**: Encryption keys stored with proper file permissions (600)
- **Validation**: Full Pydantic model validation before encryption

## Historical Content
Existing journal files and reviews are preserved in:
```
data/gemjournals/
```

## For Developers
- New model-generated journals: `data/journal/` (encrypted format)
- Historical reviews/poetry: `data/gemjournals/` (JSON format)
- Migration tools available in `scripts/encrypted_storage_demo.py`

This directory supports the enhanced encrypted storage system for secure, optimized journal creation by the Emergent Companion.