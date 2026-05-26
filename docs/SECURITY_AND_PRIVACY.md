# Security and Privacy Notes

Python Live QA Studio is a portfolio demo, but it still treats output safety seriously.

## What Is Redacted

The runtime output passes through a redaction layer before it reaches the web UI.

Current redaction targets:

- machine-specific absolute paths;
- temporary execution paths;
- common token-like strings;
- common secret assignment patterns.

This matters because developer tools often display tracebacks, environment details, file paths, and command output. Those details are useful during local debugging, but they should not appear in public screenshots, README files, or portfolio material.

## Design Rule

The public demo should explain the bug without exposing the developer's machine.

Example:

```text
File "<local-path>", line 4, in <module>
```

instead of showing a real local directory.

## Current Limitations

The redaction layer is intentionally simple and deterministic. It is useful for portfolio screenshots and common runtime output, but it is not a replacement for a full security review.

Before publishing screenshots or logs, the output should still be reviewed by a person.

