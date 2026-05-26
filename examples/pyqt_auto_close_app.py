"""Small PyQt6 example that can finish inside the MVP runner.

The important idea is `QTimer.singleShot(2000, app.quit)`: it schedules the
application to close after two seconds. Python Live QA Studio detects that
timer and extends the runner timeout slightly so the event loop can exit
normally instead of being treated as an infinite loop.
"""

from __future__ import annotations

import sys

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget


def build_window() -> QWidget:
    """Create the demo window without starting the application event loop."""

    window = QWidget()
    window.setWindowTitle("Python Live QA Studio Preview")
    window.setFixedSize(320, 320)

    layout = QVBoxLayout()
    label = QLabel("Live preview concept")
    layout.addWidget(label)
    window.setLayout(layout)
    return window


def main() -> int:
    """Start the PyQt6 app and close it automatically after two seconds."""

    app = QApplication(sys.argv)
    window = build_window()
    window.show()

    # The timer avoids an endless event loop during snippet execution.
    QTimer.singleShot(2000, app.quit)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
