# FileChecker

A lightweight, safety‑focused file validation utility designed for automation workflows and DevOps environments.  
It classifies files, validates extensions, applies rule‑based checks, and ensures predictable behavior in pipelines.

---

## Features

- Rule‑based file validation  
- Normalized extension handling  
- Safe execution wrapper to prevent unexpected crashes  
- Clear classification logic for different file types  
- Designed for automation, monitoring, and batch processing workflows  

---

## Why This Exists

In real environments, automation pipelines often break because of:
- Unexpected file extensions  
- Misclassified files  
- Silent failures  
- Inconsistent validation logic  

**FileChecker** provides a predictable, centralized validation layer that prevents those issues.

---

## How It Works

1. **Classify the file**  
   Determines the file type based on extension and known rules.

2. **Normalize the extension**  
   Ensures `.TXT`, `.txt`, `.Txt` all behave consistently.

3. **Apply validation rules**  
   Each file type has a rule set (size limits, allowed extensions, etc).

4. **Safe execution wrapper**  
   Prevents exceptions from crashing the pipeline.

---

## Example Usage

```python
from filechecker import classify_file, validate_file

result = validate_file("reports/data.txt")

if result.is_valid:
    print("File is valid:", result.details)
else:
    print("Invalid file:", result.error)
