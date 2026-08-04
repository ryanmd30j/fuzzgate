# fuzzgate: Continuous Fuzzing Pipeline for CI/CD

`fuzzgate` is an automated, non-intrusive CI/CD security build gate designed to run bounded fuzz testing against C/C++ targets within GitHub Actions. It leverages LLVM `libFuzzer` and AddressSanitizer (ASan) to catch memory safety vulnerabilities before code reaches production.

---

## Key Features

* **Bounded Execution (R.1):** Enforces strict per-target time budgets to prevent CI pipeline hangs.
* **Parallel Matrix Jobs (R.2 & R.8):** Executes target fuzzing loops concurrently using GitHub Actions strategy matrices.
* **State & Corpus Isolation (R.3):** Manages per-target corpus state isolated across build runs.
* **Cryptographic Target Selection (R.5):** Uses SHA-256 binary checksum hashing to bypass unmodified targets, drastically reducing CI compute time.
* **Automated Failure Gate (R.6):** Intercepts memory corruption errors (e.g., heap-buffer-overflow) and blocks deployment by returning non-zero exit codes.
* **Actionable Reporting & Artifact Storage (R.7):** Parses raw ASan crash outputs into Markdown summaries posted directly to `GITHUB_STEP_SUMMARY` and uploads crashing inputs as build artifacts.

---

## Directory Structure

```text
fuzzgate/
├── .github/workflows/
│   └── fuzz.yml            # Main GitHub Actions pipeline config
├── examples/
│   ├── clean_target/       # Safe C++ target example
│   └── vulnerable_target/  # Vulnerable C++ target (contains intentional ASan bug)
├── src/
│   ├── fuzz_wrapper.py     # Process orchestration & CLI execution controller
│   ├── target_select.py    # SHA-256 target change detection engine
│   └── report_parser.py    # ASan log parser & GitHub Step Summary generator
├── fuzz-config.yml         # Declarative YAML configuration
└── README.md<!-- Controlled experiment Run B trigger -->
