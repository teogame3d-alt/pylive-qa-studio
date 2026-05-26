# Architecture

Python Live QA Studio is split into small components so each behavior can be tested without needing the full UI.

## Components

- `LiveCodeAnalyzer`: parses Python source and returns deterministic diagnostics.
- `ConceptPredictor`: infers whether the developer likely needs a table, chart, UI, or style preview.
- `TracebackExplainer`: converts common runtime failures into actionable feedback.
- `ExecutionPolicy`: decides whether a snippet should use a standard timeout, a UI auto-close timeout, or a long-running-app warning.
- `PythonSnippetRunner`: executes snippets in a subprocess with timeout protection.
- `redaction.py`: removes machine-specific paths and common secret patterns from demo output.
- CLI: proves the core can be used before the full desktop interface exists.
- Web demo: shows the same core behavior in a review-friendly browser interface.

## Design Principles

- Keep explanations evidence-based.
- Prefer deterministic rules before optional generated explanations.
- Make every diagnostic testable.
- Separate source analysis from execution.
- Treat UI preview as an adapter, not as the core engine.
- Keep portfolio screenshots safe by redacting local machine details before rendering output.

## Planned UI Layer

The future PyQt6 interface will use a split layout:

- editor panel;
- diagnostics panel;
- preview panel;
- concept prediction panel.

The UI should consume the same core services used by tests and CLI, so behavior remains reproducible.
