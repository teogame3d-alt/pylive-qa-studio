"""Execution planning for safe, explainable snippet runs."""

from __future__ import annotations

import ast

from pylive_qa_studio.core.models import RunPlan


class ExecutionPolicy:
    """Choose a timeout strategy before running user code.

    The runner is intentionally conservative because it executes snippets in a
    subprocess. A normal expression can finish quickly, but a GUI application,
    local server, input loop, or infinite loop can run forever. This class makes
    that decision visible and testable.
    """

    default_timeout = 2.0
    max_timeout = 8.0
    ui_timer_buffer = 1.5

    def plan(self, source: str) -> RunPlan:
        """Return the run plan that should be used for the given source."""

        try:
            tree = ast.parse(source)
        except SyntaxError:
            return RunPlan(
                mode="syntax-check-first",
                timeout_seconds=self.default_timeout,
                reason="The source has syntax errors; analyze should explain them before execution.",
            )

        event_loop_line = self._find_event_loop_line(tree)
        auto_close_ms = self._find_auto_close_timer_ms(tree)

        if event_loop_line and auto_close_ms is not None:
            timeout = min(self.max_timeout, max(self.default_timeout, auto_close_ms / 1000 + self.ui_timer_buffer))
            return RunPlan(
                mode="ui-auto-close",
                timeout_seconds=round(timeout, 2),
                reason=(
                    "Detected a GUI event loop with an auto-close timer. "
                    "The runner extends the timeout so the window can quit cleanly."
                ),
                expected_to_timeout=False,
                auto_close_ms=auto_close_ms,
            )

        if event_loop_line:
            return RunPlan(
                mode="long-running-ui",
                timeout_seconds=self.default_timeout,
                reason=(
                    "Detected a GUI event loop without a visible auto-close timer. "
                    "The snippet may keep running until the safety timeout stops it."
                ),
                expected_to_timeout=True,
            )

        return RunPlan(
            mode="standard-snippet",
            timeout_seconds=self.default_timeout,
            reason="No long-running event loop was detected; use the standard snippet timeout.",
        )

    def _find_event_loop_line(self, tree: ast.AST) -> int | None:
        """Return the line that starts a known event loop, when present."""

        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr in {"exec", "exec_", "mainloop"}:
                    return getattr(node, "lineno", 1)
        return None

    def _find_auto_close_timer_ms(self, tree: ast.AST) -> int | None:
        """Detect simple auto-close timers such as QTimer.singleShot(2000, app.quit)."""

        timers: list[int] = []
        for node in ast.walk(tree):
            if not self._is_single_shot_timer(node):
                continue
            if not node.args:
                continue
            first_arg = node.args[0]
            if isinstance(first_arg, ast.Constant) and isinstance(first_arg.value, int):
                timers.append(first_arg.value)
        return min(timers) if timers else None

    def _is_single_shot_timer(self, node: ast.AST) -> bool:
        """Return True for calls that look like a one-shot UI timer."""

        return (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "singleShot"
        )
