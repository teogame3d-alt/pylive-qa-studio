"""Traceback explanation helpers with deterministic fallback rules."""

from __future__ import annotations

from pylive_qa_studio.core.models import Diagnostic
from pylive_qa_studio.core.redaction import redact_sensitive_text


class TracebackExplainer:
    """Convert common Python tracebacks into actionable diagnostics."""

    def explain(self, traceback_text: str) -> Diagnostic:
        """Explain a traceback using compact, testable rules."""

        raw_text = traceback_text.strip()
        line_number = self._extract_last_line_number(raw_text)
        text = redact_sensitive_text(raw_text)
        lowered = text.lower()

        if "execution timed out" in lowered or "timed out" in lowered:
            return Diagnostic(
                line=line_number,
                severity="error",
                code="RUNTIME-TIMEOUT",
                message="The code kept running until the safety timeout stopped it.",
                suggestion=(
                    "This often happens with GUI event loops such as app.exec() or mainloop(), "
                    "web servers, input loops, or infinite loops. Use Analyze for full applications; "
                    "use Run Snippet for short code, data checks, and functions that finish."
                ),
                evidence=self._last_non_empty_line(text),
            )
        if "filenotfounderror" in lowered:
            return Diagnostic(
                line=line_number,
                severity="error",
                code="RUNTIME-FILE-NOT-FOUND",
                message="Python could not find a file at the path used by the code.",
                suggestion="Check the current working directory and prefer pathlib with a path relative to __file__.",
                evidence=self._last_non_empty_line(text),
            )
        if "modulenotfounderror" in lowered:
            return Diagnostic(
                line=line_number,
                severity="error",
                code="RUNTIME-MODULE-NOT-FOUND",
                message="The environment cannot import one of the requested modules.",
                suggestion="Confirm the virtual environment is active and install the dependency in that same environment.",
                evidence=self._last_non_empty_line(text),
            )
        if "nameerror" in lowered:
            return Diagnostic(
                line=line_number,
                severity="error",
                code="RUNTIME-NAME-ERROR",
                message="The code uses a name before Python knows what it refers to.",
                suggestion="Check spelling, import order, assignment order, and whether the variable is inside another scope.",
                evidence=self._last_non_empty_line(text),
            )
        if "keyerror" in lowered:
            return Diagnostic(
                line=line_number,
                severity="error",
                code="RUNTIME-KEY-ERROR",
                message="A dictionary, dataframe, or mapping was accessed with a missing key.",
                suggestion="Print available keys or columns before indexing, then validate required fields early.",
                evidence=self._last_non_empty_line(text),
            )

        return Diagnostic(
            line=line_number,
            severity="error",
            code="RUNTIME-UNKNOWN",
            message="Python raised an error that is not covered by the current MVP rules.",
            suggestion="Read the final traceback line first, then inspect the nearest project line above it.",
            evidence=self._last_non_empty_line(text),
        )

    def _extract_last_line_number(self, text: str) -> int:
        line_number = 1
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith('File "') and ", line " in stripped:
                try:
                    line_number = int(stripped.split(", line ", 1)[1].split(",", 1)[0])
                except ValueError:
                    continue
        return line_number

    def _last_non_empty_line(self, text: str) -> str:
        for line in reversed(text.splitlines()):
            if line.strip():
                return line.strip()
        return ""
