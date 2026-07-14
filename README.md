# fuzzgate

Time-bounded fuzz testing for CI/CD pipelines.

fuzzgate runs coverage-guided fuzzing inside GitHub Actions, catching vulnerabilities
during automated builds without requiring hours-long fuzzing campaigns.

## Status
Work in progress. MSc dissertation project, 2026.

## Planned features
- Configurable time budget so the fuzz stage fits inside a normal build
- Target selection: skip fuzz targets that have not changed since the last run
- Developer-readable crash reports (what crashed, the input that caused it, where)
- Configurable severity threshold to decide whether a crash blocks the build