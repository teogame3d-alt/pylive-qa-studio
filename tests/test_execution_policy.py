from pylive_qa_studio.core.execution_policy import ExecutionPolicy


def test_policy_uses_standard_timeout_for_short_snippets():
    plan = ExecutionPolicy().plan("print('hello')\n")

    assert plan.mode == "standard-snippet"
    assert plan.timeout_seconds == 2.0
    assert not plan.expected_to_timeout


def test_policy_extends_timeout_for_ui_auto_close_timer():
    source = """
from PyQt6.QtCore import QTimer
app.exec()
QTimer.singleShot(2000, app.quit)
"""

    plan = ExecutionPolicy().plan(source)

    assert plan.mode == "ui-auto-close"
    assert plan.auto_close_ms == 2000
    assert plan.timeout_seconds > 2.0
    assert not plan.expected_to_timeout


def test_policy_warns_for_ui_without_auto_close_timer():
    plan = ExecutionPolicy().plan("app.exec()\n")

    assert plan.mode == "long-running-ui"
    assert plan.expected_to_timeout
