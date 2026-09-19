import os
import json
import hashlib
from pathlib import Path
from dataclasses import dataclass
from pathlib import Path
from enum import Enum

# ANSI colors for terminal output
RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
BLUE = "\033[34m"

class ValidationStatus(Enum):
    OK = "ok"
    WARNING = "warning"
    ERROR = "error"
    
class ChangeStatus(Enum):
    NEW = "new"
    CHANGED = "changed"
    UNCHANGED = "unchanged"
    DELETED = "DELETED"

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
    
def colorize_change(change_status):
    if change_status == ChangeStatus.NEW:
        return GREEN
    elif change_status == ChangeStatus.CHANGED:
        return YELLOW
    elif change_status == ChangeStatus.DELETED:
        return RED
    else:
        return BLUE  # Unchanged    
    
def format_result(result: FileCheckResult) -> str:
    # Normalize status to a string
    if isinstance(result.status, str):
        status_text = result.status.upper()
    else:
        status_text = result.status.value.upper()
        
    if status_text == "OK":
        status_color = GREEN
    elif status_text == "ERROR":
        status_color = RED
    else:
        status_color = YELLOW
    
    header = f"{CYAN}=== {result.file} ({result.type}) ==={RESET}"
    status_line = f"Status:       {status_color}{status_text}{RESET}"
    change_text = result.change.value.capitalize()
    change_color = colorize_change(result.change)
        
    return (
        f"\n{header}\n"
        f"{status_line}\n"
        f"Change:       {change_color}{change_text}{RESET}\n"
        f"MD5:          {result.md5}\n"
        f"SHA256:       {result.sha256}\n"
        f"Size:         {result.size} bytes\n"
        f"Modified:     {result.modified}\n"
        f"Details:      {result.details}\n"
    )

BASELINE_FILE = "baseline.json"

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
        
def reset_baseline():
    baseline_file = "baseline.json"
    if os.path.exists(baseline_file):
        os.remove(baseline_file)
    # Optional: recreate empty baseline
    save_baseline({})
        
        # --- Change Detection ---
def determine_change(result: FileCheckResult, baseline: dict) -> ChangeStatus:
    previous = baseline.get(result.file)

    if previous is None:
        return ChangeStatus.NEW

    if previous["sha256"] == result.sha256:
        return ChangeStatus.UNCHANGED

    return ChangeStatus.CHANGED

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

def validate_file(context: RuleContext):
    rule = RULES.get(context.file_type)
    
    if rule:
        return safe_execute(rule, context)
    return {
        "status": ValidationStatus.OK, 
        "details": "No rules for this file type"
		}

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

RULES = {
    "json": validate_json,
    "dll": validate_dll,
    "text": validate_text,
    "log": validate_log,
}

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
        
        previous_info = baseline.get(file_path.name)
        
        context = RuleContext(
            path=file_path,
            file_type=file_type,
            previous_info=previous_info,
            baseline=baseline
        )
        
        validation = validate_file(context)
        hashes = compute_hashes(file_path)

        current_info = {
            "md5": hashes.get("md5"),
            "sha256": hashes.get("sha256"),
            "size": file_path.stat().st_size,
            "modified": file_path.stat().st_mtime,
}

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
        
    # --- Detect deleted files ---
    current_files = {r.file for r in results}

    for old_file, old_meta in baseline.items():
        if old_file not in current_files:
            results.append(FileCheckResult(
                file=old_file,
                type="unknown",
                change=ChangeStatus.DELETED,
                md5=old_meta.get("md5", ""),
                sha256=old_meta.get("sha256", ""),
                size=old_meta.get("size", 0),
                modified=old_meta.get("modified", 0),
                status=ValidationStatus.OK,
                details="File existed in baseline but is missing now",
            ))        
        
        
    new_baseline = {r.file: {
        "md5": r.md5,
        "sha256": r.sha256,
        "size": r.size,
        "modified": r.modified,
    } for r in results}
    
    save_baseline(new_baseline)
    return results

def main():
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(
        description="FileCheckerCache — validate files, compute hashes, and compare baselines."
    )

    parser.add_argument(
        "folder",
        nargs="?",
        default="testdata",
        help="Folder to scan for files"
    )
    
    parser.add_argument(
        "--reset-baseline",
        action="store_true",
        help="Reset the baseline before scanning"
    )

    args = parser.parse_args()
    folder_path = str(Path(args.folder).resolve())
    
    if args.reset_baseline:
        reset_baseline()

    results = run_filechecker(folder_path)

    for r in results:
        print(format_result(r))

    ok_count = sum(1 for r in results if r.status == ValidationStatus.OK)
    error_count = sum(1 for r in results if str(r.status).lower() == "error")
    total = len(results)

    ok_color = GREEN if ok_count > 0 else RESET
    err_color = RED if error_count > 0 else RESET

    print(f"\nSummary:")
    print(f"  OK:     {ok_color}{ok_count}{RESET}")
    print(f"  Errors: {err_color}{error_count}{RESET}")
    print(f"  Total:  {total}")


if __name__ == "__main__":
    main()
