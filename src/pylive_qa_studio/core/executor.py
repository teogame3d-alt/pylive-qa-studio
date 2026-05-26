"""Controlled snippet execution for preview-oriented workflows."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from pylive_qa_studio.core.execution_policy import ExecutionPolicy
from pylive_qa_studio.core.models import ExecutionResult
from pylive_qa_studio.core.redaction import redact_sensitive_text


class PythonSnippetRunner:
    """Run Python snippets in a subprocess and capture the result."""

    def run(self, source: str, timeout: float | None = None, cwd: Path | None = None) -> ExecutionResult:
        """Execute source code in a temporary file with a timeout.

        When `timeout` is omitted, the runner asks `ExecutionPolicy` for a safe
        plan. This lets short snippets stay fast while UI snippets with
        `QTimer.singleShot(..., app.quit)` get enough time to close cleanly.
        """

        timeout = timeout if timeout is not None else ExecutionPolicy().plan(source).timeout_seconds

        with tempfile.TemporaryDirectory(prefix="pylive_qa_") as tmp_dir:
            script_path = Path(tmp_dir) / "snippet.py"
            script_path.write_text(source, encoding="utf-8")

            try:
                # The subprocess prevents user code from sharing state with the
                # demo server and gives us one place to enforce the timeout.
                completed = subprocess.run(
                    [sys.executable, str(script_path)],
                    cwd=str(cwd) if cwd else None,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    check=False,
                )
            except subprocess.TimeoutExpired as exc:
                return ExecutionResult(
                    return_code=124,
                    stdout=redact_sensitive_text(exc.stdout or ""),
                    stderr=redact_sensitive_text(exc.stderr or "Execution timed out."),
                    timed_out=True,
                )

        return ExecutionResult(
            return_code=completed.returncode,
            stdout=redact_sensitive_text(completed.stdout),
            stderr=redact_sensitive_text(completed.stderr),
        )
