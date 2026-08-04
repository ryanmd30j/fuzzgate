#!/usr/bin/env python3
import subprocess
import sys
import argparse
import os

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

from target_select import check_target_changed
from report_parser import parse_asan_log, append_to_github_step_summary

def load_yaml_config(config_path):
    """Loads configuration settings from fuzz-config.yml."""
    if not HAS_YAML:
        print("[-] PyYAML not installed. Using CLI arguments fallback.", file=sys.stderr)
        return {}
    if not os.path.exists(config_path):
        return {}
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def run_bounded_fuzzing(target, timeout_seconds, skip_unchanged=True):
    if not os.path.exists(target):
        print(f"[-] Error: Target binary '{target}' not found.", file=sys.stderr)
        sys.exit(1)

    target_name = os.path.basename(target)

    # Requirement R.5: Target Selection Check
    if skip_unchanged and not check_target_changed(target):
        print(f"[+] SKIPPING FUZZING: Target '{target}' is identical to previous build.")
        sys.exit(0)

    print(f"[+] Launching fuzzgate Bounded Fuzzer: {target}")
    print(f"[+] Enforcing Time Budget: {timeout_seconds} seconds")

    cmd = [target, f"-max_total_time={timeout_seconds}"]
    
    target_dir = os.path.dirname(target)
    target_corpus = os.path.join(target_dir, "corpus")
    
    if os.path.exists(target_corpus):
        print(f"[+] Using target corpus directory: {target_corpus}")
        cmd.append(target_corpus)

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout_seconds + 5
        )

        print(result.stdout)
        print(result.stderr, file=sys.stderr)

        if result.returncode != 0 or "ERROR: AddressSanitizer" in result.stderr or "SUMMARY:" in result.stderr:
            print("\n[!] BUILD GATE FAILED: Vulnerability Detected by ASan!", file=sys.stderr)
            
            # Requirement R.7: Actionable Markdown Report
            md_report = parse_asan_log(result.stderr, target_name)
            append_to_github_step_summary(md_report)
            
            sys.exit(1)

        print("\n[+] Campaign finished cleanly: No crashes detected within time limit.")
        sys.exit(0)

    except subprocess.TimeoutExpired:
        print("\n[+] Time Budget Reached: Campaign completed without finding a crash.")
        sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="fuzzgate Process Controller")
    parser.add_argument("--target", required=True, help="Path to compiled target binary")
    parser.add_argument("--timeout", type=int, default=60, help="Time budget in seconds")
    parser.add_argument("--skip-unchanged", action="store_true", help="Enable R.5 target selection")
    parser.add_argument("--config", default="fuzz-config.yml", help="Path to YAML configuration")
    args = parser.parse_args()
    
    # Load PyYAML config if available
    config = load_yaml_config(args.config)
    timeout = config.get("global_timeout", args.timeout)

    run_bounded_fuzzing(args.target, timeout, skip_unchanged=args.skip_unchanged)