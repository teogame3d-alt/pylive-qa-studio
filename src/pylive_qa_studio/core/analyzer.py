"""Static source analysis for fast, line-oriented Python feedback."""

from __future__ import annotations

import ast
from pathlib import PurePosixPath, PureWindowsPath

from pylive_qa_studio.core.execution_policy import ExecutionPolicy
from pylive_qa_studio.core.models import Diagnostic


class LiveCodeAnalyzer:
    """Analyze Python source and return QA-oriented diagnostics.

    The analyzer deliberately starts with deterministic rules. That makes the
    behavior easy to test and keeps AI-style explanations grounded in evidence.
    """

    def analyze(self, source: str, filename: str = "<editor>") -> list[Diagnostic]:
        """Inspect source code and return diagnostics sorted by line number."""

        try:
            tree = ast.parse(source, filename=filename)
        except SyntaxError as exc:
            return [self._syntax_error_to_diagnostic(exc)]

        diagnostics: list[Diagnostic] = []
        diagnostics.extend(self._detect_fragile_paths(tree))
        diagnostics.extend(self._detect_bare_except(tree))
        diagnostics.extend(self._detect_mutable_defaults(tree))
        diagnostics.extend(self._detect_ui_without_main_guard(tree))
        diagnostics.extend(self._detect_blocking_event_loop(tree))
        diagnostics.extend(self._detect_auto_close_timer(tree))
        return sorted(diagnostics, key=lambda item: (item.line, item.code))

    def _syntax_error_to_diagnostic(self, exc: SyntaxError) -> Diagnostic:
        message = exc.msg or "Python could not parse this line."
        suggestion = "Check punctuation, indentation, brackets, quotes, and the line directly above the reported line."
        if "expected ':'" in message:
            suggestion = "Add ':' after statements such as if, for, while, def, class, try, except, with, or match."
        if "was never closed" in message:
            suggestion = (
                "Close the matching bracket before continuing. Use () for function calls and grouping, "
                "[] for lists and indexing, and {} for dictionaries, sets, or formatted placeholders."
            )
        if "does not match opening parenthesis" in message or "does not match opening bracket" in message:
            suggestion = (
                "Match each opener with the same closer: '(' closes with ')', '[' closes with ']', and "
                "'{' closes with '}'. Check the highlighted line and the line above it."
            )
        return Diagnostic(
            line=exc.lineno or 1,
            severity="error",
            code="PY-SYNTAX",
            message=message,
            suggestion=suggestion,
            evidence=(exc.text or "").strip(),
        )

    def _detect_fragile_paths(self, tree: ast.AST) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        path_functions = {"open"}
        path_methods = {"read_csv", "read_excel", "to_csv", "to_excel", "connect"}

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not node.args:
                continue
            if not self._is_path_like_call(node, path_functions, path_methods):
                continue

            first_arg = node.args[0]
            if isinstance(first_arg, ast.Constant) and isinstance(first_arg.value, str):
                value = first_arg.value
                if self._looks_like_relative_path(value):
                    diagnostics.append(
                        Diagnostic(
                            line=getattr(node, "lineno", 1),
                            severity="warning",
                            code="PATH-PATHLIB",
                            message="Relative string paths can break when the app runs from another working directory.",
                            suggestion='Use pathlib: Path(__file__).parent / "folder" / "file.ext", then pass the Path object.',
                            evidence=value,
                        )
                    )
        return diagnostics

    def _detect_bare_except(self, tree: ast.AST) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                diagnostics.append(
                    Diagnostic(
                        line=getattr(node, "lineno", 1),
                        severity="warning",
                        code="QA-BARE-EXCEPT",
                        message="Bare except hides the real failure and makes bugs harder to reproduce.",
                        suggestion="Catch a specific exception and log the error context.",
                    )
                )
        return diagnostics

    def _detect_mutable_defaults(self, tree: ast.AST) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for default in node.args.defaults:
                if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                    diagnostics.append(
                        Diagnostic(
                            line=getattr(default, "lineno", getattr(node, "lineno", 1)),
                            severity="warning",
                            code="PY-MUTABLE-DEFAULT",
                            message="Mutable default arguments are shared between calls.",
                            suggestion="Use None as the default and create the list/dict/set inside the function.",
                            evidence=node.name,
                        )
                    )
        return diagnostics

    def _detect_ui_without_main_guard(self, tree: ast.AST) -> list[Diagnostic]:
        imports = {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
        imports.update(
            node.module or ""
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        )
        uses_ui = any(name.startswith(("tkinter", "PyQt6", "PySide6")) for name in imports)
        if not uses_ui:
            return []

        has_main_guard = any(
            isinstance(node, ast.If)
            and isinstance(node.test, ast.Compare)
            and "__name__" in ast.unparse(node.test)
            and "__main__" in ast.unparse(node.test)
            for node in ast.walk(tree)
        )
        if has_main_guard:
            return []
        return [
            Diagnostic(
                line=1,
                severity="info",
                code="UI-MAIN-GUARD",
                message="UI apps are easier to preview and test when startup code is behind a main guard.",
                suggestion='Move app startup into main() and call it under if __name__ == "__main__".',
            )
        ]

    def _detect_blocking_event_loop(self, tree: ast.AST) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                continue
            if node.func.attr not in {"exec", "exec_", "mainloop"}:
                continue
            diagnostics.append(
                Diagnostic(
                    line=getattr(node, "lineno", 1),
                    severity="info",
                    code="RUN-BLOCKING-EVENT-LOOP",
                    message="This line starts an application event loop that can keep running until the window is closed.",
                    suggestion=(
                        "Use Analyze for full UI applications. Run Snippet is designed for short code that finishes; "
                        "a future UI preview adapter should handle app windows without treating them as failures."
                    ),
                )
            )
        return diagnostics

    def _detect_auto_close_timer(self, tree: ast.AST) -> list[Diagnostic]:
        plan = ExecutionPolicy().plan(ast.unparse(tree))
        if plan.mode != "ui-auto-close" or plan.auto_close_ms is None:
            return []
        return [
            Diagnostic(
                line=1,
                severity="info",
                code="RUN-AUTO-CLOSE-TIMER",
                message=f"Detected an auto-close timer after {plan.auto_close_ms} ms.",
                suggestion=(
                    f"Run Snippet will allow about {plan.timeout_seconds:.1f} seconds so the UI can close cleanly. "
                    "If the app still times out, reduce the timer delay or move long-running work into a testable function."
                ),
            )
        ]

    def _is_path_like_call(self, node: ast.Call, functions: set[str], methods: set[str]) -> bool:
        func = node.func
        if isinstance(func, ast.Name):
            return func.id in functions
        if isinstance(func, ast.Attribute):
            return func.attr in methods
        return False

    def _looks_like_relative_path(self, value: str) -> bool:
        if value.startswith(("http://", "https://")):
            return False
        if PureWindowsPath(value).is_absolute() or PurePosixPath(value).is_absolute():
            return False
        return "/" in value or "\\" in value or "." in PurePosixPath(value).name
