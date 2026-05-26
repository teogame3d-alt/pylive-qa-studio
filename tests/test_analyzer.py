from pylive_qa_studio.core.analyzer import LiveCodeAnalyzer


def test_analyzer_reports_syntax_error_with_actionable_suggestion():
    diagnostics = LiveCodeAnalyzer().analyze("if True\n    print('missing colon')\n")

    assert diagnostics[0].code == "PY-SYNTAX"
    assert diagnostics[0].severity == "error"
    assert "Add ':'" in diagnostics[0].suggestion


def test_analyzer_explains_bracket_roles_for_unclosed_lists():
    diagnostics = LiveCodeAnalyzer().analyze("numbers = [1, 2, 3\nprint(numbers)\n")

    assert diagnostics[0].code == "PY-SYNTAX"
    assert "[] for lists" in diagnostics[0].suggestion


def test_analyzer_suggests_pathlib_for_fragile_relative_paths():
    source = 'with open("data/input.csv") as file:\n    print(file.read())\n'

    diagnostics = LiveCodeAnalyzer().analyze(source)

    assert [item.code for item in diagnostics] == ["PATH-PATHLIB"]
    assert "pathlib" in diagnostics[0].suggestion


def test_analyzer_detects_bare_except_and_mutable_default():
    source = """
def collect(items=[]):
    try:
        return items[0]
    except:
        return None
"""

    codes = {item.code for item in LiveCodeAnalyzer().analyze(source)}

    assert "PY-MUTABLE-DEFAULT" in codes
    assert "QA-BARE-EXCEPT" in codes


def test_analyzer_recommends_main_guard_for_ui_apps():
    source = "from PyQt6.QtWidgets import QApplication\napp = QApplication([])\n"

    diagnostics = LiveCodeAnalyzer().analyze(source)

    assert any(item.code == "UI-MAIN-GUARD" for item in diagnostics)


def test_analyzer_detects_blocking_ui_event_loop():
    source = "from PyQt6.QtWidgets import QApplication\napp = QApplication([])\napp.exec()\n"

    diagnostics = LiveCodeAnalyzer().analyze(source)

    assert any(item.code == "RUN-BLOCKING-EVENT-LOOP" for item in diagnostics)


def test_analyzer_detects_qtimer_auto_close_timer():
    source = """
from PyQt6.QtCore import QTimer
app.exec()
QTimer.singleShot(2000, app.quit)
"""

    diagnostics = LiveCodeAnalyzer().analyze(source)

    assert any(item.code == "RUN-AUTO-CLOSE-TIMER" for item in diagnostics)
