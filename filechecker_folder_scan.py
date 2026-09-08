import os
import json
from pathlib import Path
from dataclasses import dataclass
from pathlib import Path
from enum import Enum

class ValidationStatus(Enum):
    OK = "ok"
    WARNING = "warning"
    ERROR = "error"
    
class ChangeStatus(Enum):
    NEW = "new"
    CHANGED = "changed"
    UNCHANGED = "unchanged"

@dataclass
class RuleContext:
    path: Path
    file_type: str
    previous_info: dict | None
    baseline: dict
    
@dataclass
class FileCheckResult:
    file: str
    type: str
    change: ChangeStatus
    md5: str
    sha256: str
    size: int
    modified: float
    status: ValidationStatus
    details: str

BASELINE_FILE = "baseline.json"
RULES = {
    "json": validate_json,
    "dll": validate_dll,
    "text": validate_text,
    "log": validate_log,
}

EXTENSION_RULES = {
    ".dll": "dll",
    ".exe": "exe",
    ".config": "config",
    ".json": "json",
    ".log": "log",
    ".txt": "text",
}

def safe_execute(rule, context: RuleContext):
    """Run a rule safely and return a structured result dict."""
    try:
        return rule(context)
    except Exception as e:
        return {
            "status": "error",
            "details": f"Validator crashed: {e}"
        }

def normalize_extension(path: Path) -> str:
    """Return a clean, lowercase extension or empty string."""
    ext = path.suffix.lower().strip()
    return ext

def load_baseline():
    """Load baseline data from disk."""
    try:
        with open(BASELINE_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception:
        return {}

def save_baseline(data):
    """Save baseline data to disk."""
    try:
        with open(BASELINE_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Failed to save baseline: {e}")

def scan_folder(folder_path: str):
    """Return a list of file paths inside the folder."""
    folder = Path(folder_path)
    files = []

    for item in folder.iterdir():
        if item.is_file():
            files.append(item)

    return files

def classify_file(path: Path) -> str:
    ext = normalize_extension(path)
    return EXTENSION_RULES.get(ext, "unknown")

def validate_file(context: RuleContext, file_type: str):
    """Dispatch validation based on file type."""
    path = context.path
    rule = RULES.get(file_type)
    
    context = RuleContext(
        path=path,
        file_type=file_type,
        previous_info=baseline.get(path.name),
        baseline=baseline,
    )
    if rule:
        return safe_execute(rule, context)
    return {"status": ValidationStatus.OK, "details": "No rules for this file type"}
    if file_type == "json":
        return validate_json(path)
    elif file_type == "text":
        return validate_text(path)
    elif file_type == "dll":
        return validate_dll(path)
    elif file_type == "log":
        return validate_log(path)
    else:
        return {"status": ValidationStatus.OK, "details": "No rules for this file type"}

def validate_text(context: RuleContext):
    """Basic text file validation."""
    path = context.path
    
    try:
        content = path.read_text(errors="ignore")

        if len(content.strip()) == 0:
            return {"status": "warning", "details": "Text file is empty"}

        # Optional: check for non-ASCII characters
        if not content.isascii():
            return {"status": ValidationStatus.OK, "details": "Text file contains non-ASCII characters"}

        return {"status": ValidationStatus.OK, "details": "Text file is valid"}
    except Exception as e:
        return {"status": "error", "details": str(e)}

def validate_log(context: RuleContext):
    """Basic log file validation with error/warning detection."""
    path = context.path
    
    try:
        content = path.read_text(errors="ignore")

        if len(content.strip()) == 0:
            return {"status": "warning", "details": "Log file is empty"}

        lines = content.splitlines()

        error_count = sum(1 for line in lines if "ERROR" in line.upper())
        warning_count = sum(1 for line in lines if "WARNING" in line.upper())

        if error_count > 0:
            return {
                "status": "error",
                "details": f"Found {error_count} ERROR lines and {warning_count} WARNING lines"
            }

        if warning_count > 0:
            return {
                "status": "warning",
                "details": f"Found {warning_count} WARNING lines"
            }

        return {"status": ValidationStatus.OK, "details": "No errors or warnings detected"}

    except Exception as e:
        return {"status": "error", "details": str(e)}

def validate_json(context: RuleContext):
    """Placeholder JSON validation."""
    path = context.path
    
    try:
        import json
        with open(path, "r") as f:
            json.load(f)
        return {"status": ValidationStatus.OK, "details": "Valid JSON"}
    except Exception as e:
        return {"status": "error", "details": str(e)}

def validate_dll(context: RuleContext):
    """Placeholder DLL validation."""
    path = context.path
    return {"status": ValidationStatus.OK, "details": "DLL validation not implemented yet"}

import hashlib

def compute_hashes(path: Path):
    """Return MD5 and SHA256 hashes for a file."""
    md5 = hashlib.md5()
    sha256 = hashlib.sha256()

    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5.update(chunk)
                sha256.update(chunk)

        return {
            "md5": md5.hexdigest(),
            "sha256": sha256.hexdigest()
        }

    except Exception as e:
        return {
            "md5": None,
            "sha256": None,
            "error": str(e)
        }

def run_filechecker(folder_path: str):
    """Main entry point."""
    results = []
    baseline = load_baseline()
    
    for file_path in scan_folder(folder_path):
        file_type = classify_file(file_path)
        validation = validate_file(file_path, file_type)
        hashes = compute_hashes(file_path)

        current_info = {
            "md5": hashes.get("md5"),
            "sha256": hashes.get("sha256"),
            "size": file_path.stat().st_size,
            "modified": file_path.stat().st_mtime,
}
        previous_info = baseline.get(file_path.name)

        # Determine change status
        if previous_info is None:
            change_status = ChangeStatus.NEW
        elif previous_info["sha256"] != current_info["sha256"]:
            change_status = ChangeStatus.CHANGED
        else:
            change_status = ChangeStatus.UNCHANGED
        
        results.append(FileCheckResult(
            file=file_path.name,
            type=file_type,
            change=change_status,
            md5=current_info["md5"],
            sha256=current_info["sha256"],
            size=current_info["size"],
            modified=current_info["modified"],
            status=validation["status"],
            details=validation["details"],
        ))
        
        new_baseline = {r.file: {
            "md5": r.md5,
            "sha256": r.sha256,
            "size": r.size,
            "modified": r.modified,
        } for r in results}

    return results

if __name__ == "__main__":
    results = run_filechecker("C:\\path\\to\\your\\folder")
    for r in results:
        print(r)

