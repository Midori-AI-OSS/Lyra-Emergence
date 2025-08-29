# Journal Directory Notice

⚠️ **DEPRECATED LOCATION**

This directory is no longer used for new journal files. All journal files have been moved to `data/gemjournals/`.

**Please do not add new files to this directory.**

## New Location
All journal files are now stored in:
```
data/gemjournals/
```

## Migration Information
- All existing journal files have been migrated to the new location
- The encrypted PyTorch-compiled Pydantic storage system uses the new location
- Legacy JSON files and backups have been preserved in the new location

## For Developers
If you need to update code that references journal files, please update paths from:
- `data/journal/` → `data/gemjournals/`

This change supports the enhanced encrypted storage system and improved project organization.