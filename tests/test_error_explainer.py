from pylive_qa_studio.core.error_explainer import TracebackExplainer


def test_explainer_turns_file_not_found_into_pathlib_guidance():
    traceback_text = '''
Traceback (most recent call last):
  File "X:\\Example\\Private\\app.py", line 12, in <module>
    open("data/input.csv")
FileNotFoundError: [Errno 2] No such file or directory: "data/input.csv"
'''

    diagnostic = TracebackExplainer().explain(traceback_text)

    assert diagnostic.code == "RUNTIME-FILE-NOT-FOUND"
    assert diagnostic.line == 12
    assert "pathlib" in diagnostic.suggestion
    assert "X:\\" not in diagnostic.evidence


def test_explainer_handles_missing_module():
    diagnostic = TracebackExplainer().explain("ModuleNotFoundError: No module named 'PyQt6'")

    assert diagnostic.code == "RUNTIME-MODULE-NOT-FOUND"
    assert "virtual environment" in diagnostic.suggestion


def test_explainer_handles_execution_timeout_as_long_running_app():
    diagnostic = TracebackExplainer().explain("Execution timed out.")

    assert diagnostic.code == "RUNTIME-TIMEOUT"
    assert "GUI event loops" in diagnostic.suggestion
    assert "Run Snippet" in diagnostic.suggestion
