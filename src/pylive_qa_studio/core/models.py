"""Data models shared by the analyzer, predictor, and executor."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Severity = Literal["info", "warning", "error"]


@dataclass(frozen=True)
class Diagnostic:
    """Actionable feedback attached to a source line."""

    line: int
    severity: Severity
    code: str
    message: str
    suggestion: str
    evidence: str = ""


@dataclass(frozen=True)
class ConceptPrediction:
    """A prediction about the visual feedback the developer likely needs."""

    preview_type: str
    confidence: float
    reason: str
    suggested_next_step: str


@dataclass(frozen=True)
class ExecutionResult:
    """Result of running a Python snippet in a subprocess."""

    return_code: int
    stdout: str
    stderr: str
    timed_out: bool = False

    @property
    def ok(self) -> bool:
        """Return True when the snippet completed successfully."""

        return self.return_code == 0 and not self.timed_out


@dataclass(frozen=True)
class RunPlan:
    """Execution policy chosen before running a snippet.

    The web demo displays this object so the user can see why a snippet gets a
    short timeout, an extended timeout, or a warning about long-running apps.
    """

    mode: str
    timeout_seconds: float
    reason: str
    expected_to_timeout: bool = False
    auto_close_ms: int | None = None
