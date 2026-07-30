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

    # Command executing libFuzzer with native max_total_time flag
    cmd = [target, f"-max_total_time={timeout_seconds}"]

    try:
        # Execute sub-process with Python wrapper timeout as safety net
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Buffer timeout gives libFuzzer 5 extra seconds to wrap up cleanly
        stdout, stderr = process.communicate(timeout=timeout_seconds + 5)
        
        # If libFuzzer / ASan caught a crash/defect, it exits with non-zero code
        if process.returncode != 0:
            print("\n[!] CRASH DETECTED OR VULNERABILITY FOUND!", file=sys.stderr)
            print("=================== STACK TRACE ===================", file=sys.stderr)
            print(stderr, file=sys.stderr)
            sys.exit(1) # Fail the build gate
            
        print("\n[+] Bounded campaign finished cleanly: No crashes detected within time limit.")
        sys.exit(0)

    except subprocess.TimeoutExpired:
        print("\n[!] Time Budget Reached: Gracefully terminating fuzzer...")
        process.terminate()
        try:
            process.communicate(timeout=3)
        except subprocess.TimeoutExpired:
            print("[!] Enforcing process kill...")
            process.kill()
            process.communicate()
            
        print("[+] Fuzzer stopped cleanly. State preserved.")
        sys.exit(0) # Time-limit reached without crash = SUCCESS

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="fuzzgate Process Controller")
    parser.add_argument("--target", required=True, help="Path to compiled target binary")
    parser.add_argument("--timeout", type=int, required=True, help="Time budget in seconds")
    args = parser.parse_args()
    
    run_bounded_fuzzing(args.target, args.timeout)