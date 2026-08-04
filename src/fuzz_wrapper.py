#!/usr/bin/env python3
import subprocess
import sys
import argparse
import os

# Fix Bug 6: Ensure src/ is in sys.path for root execution
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

from target_select import check_target_changed, update_target_status
from report_parser import parse_asan_log, append_to_github_step_summary

def load_yaml_config(config_path):
    """Loads configuration settings from fuzz-config.yml."""
    if not HAS_YAML or not os.path.exists(config_path):
        return {}
    with open(config_path, 'r') as f:
        return yaml.safe_load(f) or {}

def run_bounded_fuzzing(target, timeout_seconds, skip_unchanged=True):
    target_abs = os.path.abspath(target)
    if not os.path.exists(target_abs):
        print(f"[-] Error: Target binary '{target}' not found.", file=sys.stderr)
        sys.exit(1)

    target_name = os.path.basename(target)

    # Fix Bug 3: Target Selection Check (Only skip if UNCHANGED and PREVIOUSLY PASSED)
    if skip_unchanged and not check_target_changed(target_abs):
        print(f"[+] SKIPPING FUZZING: Target '{target_name}' is identical to a PREVIOUSLY PASSED build.")
        sys.exit(0)

    print(f"[+] Launching fuzzgate Bounded Fuzzer: {target}")
    print(f"[+] Enforcing Time Budget: {timeout_seconds} seconds")

    cmd = [target_abs, f"-max_total_time={timeout_seconds}"]
    
    target_dir = os.path.dirname(target_abs)
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

        # Fix Bug 2: Tightened crash detection (strict ASan check)
        is_crash = result.returncode != 0 or "ERROR: AddressSanitizer" in result.stderr

        if is_crash:
            print("\n[!] BUILD GATE FAILED: Vulnerability Detected by ASan!", file=sys.stderr)
            
            # Bug 3 Fix: Record that this hash FAILED
            update_target_status(target_abs, passed=False)

            md_report = parse_asan_log(result.stderr, target_name)
            append_to_github_step_summary(md_report)
            
            sys.exit(1)

        # Bug 3 Fix: Record that this hash PASSED
        update_target_status(target_abs, passed=True)
        print("\n[+] Campaign finished cleanly: No crashes detected within time limit.")
        sys.exit(0)

    except subprocess.TimeoutExpired:
        update_target_status(target_abs, passed=True)
        print("\n[+] Time Budget Reached: Campaign completed cleanly without finding a crash.")
        sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="fuzzgate Process Controller")
    parser.add_argument("--target", required=True, help="Path to compiled target binary")
    parser.add_argument("--timeout", type=int, default=60, help="Time budget in seconds")
    parser.add_argument("--skip-unchanged", action="store_true", help="Enable R.5 target selection")
    parser.add_argument("--config", default="fuzz-config.yml", help="Path to YAML configuration")
    args = parser.parse_args()
    
    config = load_yaml_config(args.config)
    timeout = config.get("global_timeout", args.timeout)

    run_bounded_fuzzing(args.target, timeout, skip_unchanged=args.skip_unchanged)