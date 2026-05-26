# Test Strategy

The MVP focuses on repeatable rules that are useful for QA and debugging workflows.

## Current Test Types

- Syntax diagnostics.
- Path handling diagnostics.
- Bare exception detection.
- Mutable default argument detection.
- UI main-guard recommendation.
- Blocking UI event loop warning for snippets that start `app.exec()` or `mainloop()`.
- Execution policy for standard snippets, long-running UI apps, and UI apps with auto-close timers.
- Concept prediction for data, chart, UI, and style workflows.
- Traceback explanation.
- Timeout explanation for long-running apps, servers, input loops, or infinite loops.
- Output redaction for local paths and common secret patterns.
- Subprocess execution success and failure.
- Web demo endpoints that use the real analyzer and runner.

## Why This Matters

For a developer tool, trust is critical. If the assistant warns about a bug, the warning must be explainable and reproducible.

## Future Coverage

- Golden-file tests for CLI output.
- Fixture projects for PyQt6, Tkinter, pandas, and seaborn examples.
- Timeout and long-running snippet behavior.
- Multi-file project analysis.
- Regression tests for every new diagnostic rule.
