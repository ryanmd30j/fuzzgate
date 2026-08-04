#!/usr/bin/env python3
import hashlib
import os
import sys
import argparse

def compute_sha256(filepath):
    """Generates SHA-256 checksum of a binary file."""
    if not os.path.exists(filepath):
        print(f"[-] Error: Target file '{filepath}' does not exist.", file=sys.stderr)
        return None

    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def check_target_changed(target_path, hash_cache_dir=".fuzz_cache"):
    """
    Returns True if target should be fuzzed (changed OR previously failed).
    Returns False ONLY if target is identical AND previously passed.
    """
    current_hash = compute_sha256(target_path)
    if not current_hash:
        return True

    os.makedirs(hash_cache_dir, exist_ok=True)
    target_name = os.path.basename(target_path)
    cache_file = os.path.join(hash_cache_dir, f"{target_name}.hash")
    status_file = os.path.join(hash_cache_dir, f"{target_name}.status")

    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            previous_hash = f.read().strip()
        
        # Check previous build status if hash matches
        if current_hash == previous_hash:
            if os.path.exists(status_file):
                with open(status_file, 'r') as f:
                    last_status = f.read().strip()
                if last_status == "FAIL":
                    print(f"[!] Target Selection (R.5): '{target_name}' is unchanged BUT PREVIOUSLY FAILED. Re-running fuzzing!")
                    return True # Force re-test on vulnerable binaries
            
            print(f"[=] Target Selection (R.5): '{target_name}' is UNCHANGED and PASSED previously (SHA256: {current_hash[:8]}...).")
            return False

    return True

def update_target_status(target_path, passed=True, hash_cache_dir=".fuzz_cache"):
    """Saves the current target hash and execution result (PASS/FAIL) to cache."""
    current_hash = compute_sha256(target_path)
    if not current_hash:
        return

    os.makedirs(hash_cache_dir, exist_ok=True)
    target_name = os.path.basename(target_path)
    cache_file = os.path.join(hash_cache_dir, f"{target_name}.hash")
    status_file = os.path.join(hash_cache_dir, f"{target_name}.status")

    with open(cache_file, 'w') as f:
        f.write(current_hash)

    with open(status_file, 'w') as f:
        f.write("PASS" if passed else "FAIL")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="fuzzgate Target Selection Engine")
    parser.add_argument("--target", required=True, help="Path to compiled target binary")
    parser.add_argument("--cache-dir", default=".fuzz_cache", help="Directory storing target hashes")
    args = parser.parse_args()

    changed = check_target_changed(args.target, args.cache_dir)
    sys.exit(0 if not changed else 1)