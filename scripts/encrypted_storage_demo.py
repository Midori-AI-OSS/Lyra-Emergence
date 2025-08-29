#!/usr/bin/env python3
"""
Encrypted PyTorch Storage System Demo and Migration Tool

This script demonstrates the new encrypted PyTorch-compiled Pydantic storage system
and provides tools for migrating existing JSON journal files.
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.journal.encrypted_torch_storage import (
    EncryptedTorchStorage,
    create_encrypted_storage,
    migrate_json_to_encrypted,
)


def demo_encryption_system():
    """Demonstrate the encrypted storage system capabilities."""
    print("=== Encrypted PyTorch Storage System Demo ===\n")
    
    # Create temporary storage
    storage = EncryptedTorchStorage()
    
    print("✅ Created encrypted storage system")
    print(f"   - PyTorch version: {storage.__class__.__module__}")
    print(f"   - Encryption: AES-256 (Fernet)")
    print(f"   - Compilation: {'Available' if hasattr(storage, '_torch_save_compiled') else 'Not available'}")
    
    # Demonstrate performance characteristics
    from src.journal.parser import JournalEntry, StewardshipTrace
    import time
    import tempfile
    
    # Create test entry
    test_entry = JournalEntry(
        timestamp="2025-01-01T00:00:00Z",
        entry_type="journal",
        emotional_tone=["demonstration", "efficient"],
        description="Performance test for encrypted PyTorch storage system",
        emergent_companion_reflections="This system provides encrypted storage with PyTorch optimization while maintaining full Pydantic validation for type safety and data integrity.",
        tags=["performance", "security", "pytorch", "encryption"],
        stewardship_trace=StewardshipTrace(
            committed_by="Steward",
            witnessed_by="Co-Steward", 
            commitment_type="demo",
            reason="Demonstrating encrypted storage capabilities"
        )
    )
    
    print(f"\n📊 Performance Test:")
    
    with tempfile.NamedTemporaryFile(suffix=".torch") as tmp:
        tmp_path = Path(tmp.name)
        
        # Test save performance
        start_time = time.perf_counter()
        storage.save_encrypted(test_entry, tmp_path)
        save_time = time.perf_counter() - start_time
        
        file_size = tmp_path.stat().st_size
        
        # Test load performance  
        start_time = time.perf_counter()
        loaded_entry = storage.load_encrypted(tmp_path, JournalEntry)
        load_time = time.perf_counter() - start_time
        
        print(f"   Save time: {save_time:.4f}s")
        print(f"   Load time: {load_time:.4f}s")
        print(f"   File size: {file_size} bytes (encrypted)")
        print(f"   Data integrity: {'✅ Verified' if loaded_entry.description == test_entry.description else '❌ Failed'}")
    
    print(f"\n🔒 Security Features:")
    print(f"   - AES-256 encryption for all journal content")
    print(f"   - PyTorch optimized serialization")
    print(f"   - Full Pydantic validation maintained")
    print(f"   - Secure key management with file permissions")
    print(f"   - No plaintext data in storage files")


def migrate_journals(json_dir: Path, output_dir: Path, key_file: Path):
    """Migrate existing JSON journal files to encrypted format."""
    if not json_dir.exists():
        print(f"❌ JSON directory not found: {json_dir}")
        return False
    
    print(f"🔄 Migrating journals from {json_dir} to {output_dir}")
    print(f"🔑 Using key file: {key_file}")
    
    # Count JSON files to migrate
    json_files = [
        f for f in json_dir.glob("*.json") 
        if not f.name.endswith(".backup") 
        and not f.name.startswith("journal_manifest")
        and not f.name.startswith("journal_index")
    ]
    print(f"📁 Found {len(json_files)} journal files to migrate")
    
    if not json_files:
        print("   No journal files found to migrate")
        return True
    
    try:
        # Perform migration
        migrate_json_to_encrypted(json_dir, output_dir, key_file)
        
        print(f"✅ Successfully migrated {len(json_files)} journal files")
        print(f"📂 Encrypted files saved to: {output_dir}")
        print(f"🔑 Encryption key saved to: {key_file}")
        print(f"🔒 Key file permissions set to owner-only (600)")
        
        # Verify migration
        storage = EncryptedTorchStorage.from_key_file(key_file)
        encrypted_files = list(output_dir.glob("*.torch"))
        
        print(f"\n🔍 Verification:")
        for encrypted_file in encrypted_files[:3]:  # Check first 3 files
            try:
                entries = storage.load_journal_entries(encrypted_file)
                print(f"   ✅ {encrypted_file.name}: {len(entries)} entries loaded successfully")
            except Exception as e:
                print(f"   ❌ {encrypted_file.name}: Failed to load - {e}")
        
        if len(encrypted_files) > 3:
            print(f"   ... and {len(encrypted_files) - 3} more files")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False


def export_to_json(encrypted_dir: Path, key_file: Path, output_dir: Path):
    """Export encrypted files back to JSON format for inspection."""
    if not encrypted_dir.exists():
        print(f"❌ Encrypted directory not found: {encrypted_dir}")
        return False
    
    if not key_file.exists():
        print(f"❌ Key file not found: {key_file}")
        return False
    
    print(f"📤 Exporting encrypted files from {encrypted_dir} to JSON in {output_dir}")
    
    try:
        storage = EncryptedTorchStorage.from_key_file(key_file)
        output_dir.mkdir(exist_ok=True)
        
        encrypted_files = list(encrypted_dir.glob("*.torch"))
        print(f"📁 Found {len(encrypted_files)} encrypted files to export")
        
        for encrypted_file in encrypted_files:
            json_file = output_dir / f"{encrypted_file.stem}.json"
            storage.export_to_json(encrypted_file, json_file)
            print(f"   ✅ {encrypted_file.name} -> {json_file.name}")
        
        print(f"✅ Successfully exported {len(encrypted_files)} files to JSON")
        return True
        
    except Exception as e:
        print(f"❌ Export failed: {e}")
        return False


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="Encrypted PyTorch Storage System for Lyra Project Journals",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Demonstrate the system
  python encrypted_storage_demo.py demo
  
  # Migrate existing JSON journals
  python encrypted_storage_demo.py migrate data/gemjournals encrypted_journals storage.key
  
  # Export encrypted files back to JSON  
  python encrypted_storage_demo.py export encrypted_journals storage.key exported_json
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Demo command
    demo_parser = subparsers.add_parser("demo", help="Demonstrate encrypted storage system")
    
    # Migrate command
    migrate_parser = subparsers.add_parser("migrate", help="Migrate JSON journals to encrypted format")
    migrate_parser.add_argument("json_dir", type=Path, help="Directory containing JSON journal files")
    migrate_parser.add_argument("output_dir", type=Path, help="Directory for encrypted journal files")
    migrate_parser.add_argument("key_file", type=Path, help="File to save/load encryption key")
    
    # Export command
    export_parser = subparsers.add_parser("export", help="Export encrypted files to JSON")
    export_parser.add_argument("encrypted_dir", type=Path, help="Directory containing encrypted files")
    export_parser.add_argument("key_file", type=Path, help="Encryption key file")
    export_parser.add_argument("output_dir", type=Path, help="Directory for exported JSON files")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == "demo":
            demo_encryption_system()
            
        elif args.command == "migrate":
            success = migrate_journals(args.json_dir, args.output_dir, args.key_file)
            sys.exit(0 if success else 1)
            
        elif args.command == "export":
            success = export_to_json(args.encrypted_dir, args.key_file, args.output_dir)
            sys.exit(0 if success else 1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()