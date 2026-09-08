import os
from pathlib import Path

EXTENSION_RULES = {
    ".dll": "dll",
    ".exe": "exe",
    ".config": "config",
    ".json": "json",
    ".log": "log",
}

def scan_folder(folder_path: str):
    """Return a list of file paths inside the folder."""
    folder = Path(folder_path)
    files = []

    for item in folder.iterdir():
        if item.is_file():
            files.append(item)

    return files

def classify_file(path: Path):
    """Return the file type based on extension."""
    ext = path.suffix.lower()
    return EXTENSION_RULES.get(ext, "unknown")

def validate_file(path: Path, file_type: str):
    """Dispatch validation based on file type."""
    if file_type == "json":
        return validate_json(path)
    elif file_type == "dll":
        return validate_dll(path)
    else:
        return {"status": "ok", "details": "No rules for this file type"}

def validate_json(path: Path):
    """Placeholder JSON validation."""
    try:
        import json
        with open(path, "r") as f:
            json.load(f)
        return {"status": "ok", "details": "Valid JSON"}
    except Exception as e:
        return {"status": "error", "details": str(e)}

def validate_dll(path: Path):
    """Placeholder DLL validation."""
    return {"status": "ok", "details": "DLL validation not implemented yet"}

def run_filechecker(folder_path: str):
    """Main entry point."""
    results = []

    for file_path in scan_folder(folder_path):
        file_type = classify_file(file_path)
        validation = validate_file(file_path, file_type)

        results.append({
            "file": file_path.name,
            "type": file_type,
            "status": validation["status"],
            "details": validation["details"],
        })

    return results

if __name__ == "__main__":
    results = run_filechecker("C:\\path\\to\\your\\folder")
    for r in results:
        print(r)

