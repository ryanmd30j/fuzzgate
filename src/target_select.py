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
        # Read in 64kb chunks to handle large binaries
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def check_target_changed(target_path, hash_cache_dir=".fuzz_cache"):
    """
    Compares target hash with last fuzzed hash.
    Returns True if target has changed (or is new), False if identical.
    """
    current_hash = compute_sha256(target_path)
    if not current_hash:
        return True # Fallback: Fuzz if hash fails

    os.makedirs(hash_cache_dir, exist_ok=True)
    target_name = os.path.basename(target_path)
    cache_file = os.path.join(hash_cache_dir, f"{target_name}.hash")

    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            previous_hash = f.read().strip()
        
        if current_hash == previous_hash:
            print(f"[=] Target Selection (R.5): '{target_name}' is UNCHANGED (SHA256: {current_hash[:8]}...).")
            return False

    # Save new hash to cache
    with open(cache_file, 'w') as f:
        f.write(current_hash)

    print(f"[!] Target Selection (R.5): '{target_name}' has CHANGED or is NEW (SHA256: {current_hash[:8]}...).")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="fuzzgate Target Selection Engine")
    parser.add_argument("--target", required=True, help="Path to compiled target binary")
    parser.add_argument("--cache-dir", default=".fuzz_cache", help="Directory storing target hashes")
    args = parser.parse_args()

    changed = check_target_changed(args.target, args.cache_dir)
    if not changed:
        # Exit code 100 signals to wrapper/workflow that target can be skipped
        sys.exit(100)
    sys.exit(0)