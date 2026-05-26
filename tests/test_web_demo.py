from pylive_qa_studio.web_demo import analyze_source, run_source


def test_web_demo_analyze_uses_real_diagnostics():
    payload = analyze_source('open("data/input.csv")\n')

    assert payload["diagnostics"][0]["code"] == "PATH-PATHLIB"
    assert "pathlib" in payload["diagnostics"][0]["suggestion"]


def test_web_demo_run_explains_runtime_error():
    payload = run_source('open("missing/file.txt")\n')

    assert payload["run_plan"]["mode"] == "standard-snippet"
    assert payload["execution"]["return_code"] != 0
    assert payload["runtime_diagnostic"]["code"] == "RUNTIME-FILE-NOT-FOUND"
