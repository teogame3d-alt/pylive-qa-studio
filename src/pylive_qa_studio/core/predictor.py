"""Predict the feedback panel a developer likely needs next."""

from __future__ import annotations

import re
import ast
from pathlib import Path

from pylive_qa_studio.core.models import ConceptPrediction


class ConceptPredictor:
    """Infer developer intent from source code and open file names."""

    def predict(self, source: str, open_files: list[Path] | None = None) -> list[ConceptPrediction]:
        """Return preview suggestions for code, data, UI, and style workflows."""

        open_files = open_files or []
        predictions: list[ConceptPrediction] = []
        signals = self._extract_code_signals(source)

        if self._has_any_signal(signals, ["pandas", "pd", "DataFrame", "read_csv", "read_excel", "sqlite3", "connect", "SELECT"]):
            predictions.append(
                ConceptPrediction(
                    preview_type="table-preview",
                    confidence=0.86,
                    reason="The code references dataframe, CSV, Excel, SQL, or SQLite concepts.",
                    suggested_next_step="Show a small table preview, column names, row count, null count, and validation warnings.",
                )
            )

        if self._has_any_signal(signals, ["matplotlib", "seaborn", "plt", "sns", "plot", "barplot", "lineplot"]):
            predictions.append(
                ConceptPrediction(
                    preview_type="chart-preview",
                    confidence=0.82,
                    reason="The code appears to create a chart or dashboard visual.",
                    suggested_next_step="Render the chart next to the editor and surface data-shape errors before execution.",
                )
            )

        if self._has_any_signal(signals, ["tkinter", "PyQt6", "PySide6", "QWidget", "QMainWindow", "QApplication"]):
            predictions.append(
                ConceptPrediction(
                    preview_type="ui-preview",
                    confidence=0.88,
                    reason="The code imports or references desktop UI concepts.",
                    suggested_next_step="Preview the window lifecycle, main widget, and likely startup function.",
                )
            )

        if any(path.name.lower() == "style.py" for path in open_files) or self._has_any_signal(signals, ["stylesheet", "setStyleSheet", "theme"]):
            predictions.append(
                ConceptPrediction(
                    preview_type="style-preview",
                    confidence=0.78,
                    reason="A style module or stylesheet concept is present.",
                    suggested_next_step="Connect style changes to the UI preview and track visual changes separately from logic.",
                )
            )

        return predictions

    def _extract_code_signals(self, source: str) -> set[str]:
        """Collect import, name, call, and attribute signals from code structure."""

        try:
            tree = ast.parse(source)
        except SyntaxError:
            return set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", source))

        signals: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    signals.add(alias.name)
                    signals.add(alias.name.split(".", 1)[0])
                    if alias.asname:
                        signals.add(alias.asname)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    signals.add(node.module)
                    signals.add(node.module.split(".", 1)[0])
                for alias in node.names:
                    signals.add(alias.name)
                    if alias.asname:
                        signals.add(alias.asname)
            elif isinstance(node, ast.Name):
                signals.add(node.id)
            elif isinstance(node, ast.Attribute):
                signals.add(node.attr)
            elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                if "SELECT " in node.value.upper():
                    signals.add("SELECT")
        return signals

    def _has_any_signal(self, signals: set[str], needles: list[str]) -> bool:
        lowered = {signal.lower() for signal in signals}
        return any(needle.lower() in lowered for needle in needles)
