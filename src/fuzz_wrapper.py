#!/usr/bin/env python3
import subprocess
import sys
import argparse
import os

def run_bounded_fuzzing(target, timeout_seconds):
    if not os.path.exists(target):
        print(f"[-] Error: Target binary '{target}' not found.", file=sys.stderr)
        sys.exit(1)

    print(f"[+] Launching fuzzgate Bounded Fuzzer: {target}")
    print(f"[+] Enforcing Time Budget: {timeout_seconds} seconds")

    cmd = [target, f"-max_total_time={timeout_seconds}"]
    if os.path.exists("corpus"):
        cmd.append("corpus")

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
            print("\n[!] BUILD GATE FAILED: Vulnerability / Crash Detected by ASan!", file=sys.stderr)
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
    args = parser.parse_args()
    
    run_bounded_fuzzing(args.target, args.timeout)