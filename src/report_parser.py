#!/usr/bin/env python3
import os
import sys
import re
import argparse

def parse_asan_log(stderr_text, target_name):
    """Parses ASan output to extract crash type, location, and stack trace."""
    crash_type = "Unknown Failure"
    location = "Unknown"
    
    # Extract ASan Error Header
    type_match = re.search(r"ERROR: AddressSanitizer: ([\w-]+)", stderr_text)
    if type_match:
        crash_type = type_match.group(1)

    # Extract Memory Location / PC
    loc_match = re.search(r"READ of size|WRITE of size|heap-buffer-overflow|stack-buffer-overflow", stderr_text)
    if loc_match:
        location = loc_match.group(0)

    # Generate Markdown Summary for GitHub Step Summary
    summary_md = f"""
## 🚨 fuzzgate Security Report: `{target_name}`

> **Status:** ❌ VULNERABILITY DETECTED  
> **Defect Type:** `{crash_type}`  
> **Memory Operation:** `{location}`  

### Stack Trace Snippet
```text
"""
    # Grab the first 15 lines of the stack trace
    lines = stderr_text.splitlines()
    trace_lines = [l for l in lines if "#" in l or "ERROR:" in l or "SUMMARY:" in l][:15]
    summary_md += "\n".join(trace_lines)
    summary_md += "\n```\n"

    return summary_md

def append_to_github_step_summary(markdown_text):
    """Appends Markdown content to $GITHUB_STEP_SUMMARY if running in GitHub Actions."""
    summary_file = os.getenv("GITHUB_STEP_SUMMARY")
    if summary_file:
        with open(summary_file, "a") as f:
            f.write(markdown_text + "\n")
        print("[+] Written report to GitHub Step Summary.")
    else:
        print(markdown_text)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="fuzzgate Crash Report Parser")
    parser.add_argument("--log", required=True, help="Path to raw stderr log file")
    parser.add_argument("--target", required=True, help="Target name")
    args = parser.parse_args()

    if os.path.exists(args.log):
        with open(args.log, "r") as f:
            log_content = f.read()
        md_report = parse_asan_log(log_content, args.target)
        append_to_github_step_summary(md_report)