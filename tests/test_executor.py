from pylive_qa_studio.core.executor import PythonSnippetRunner


def test_runner_captures_successful_output():
    result = PythonSnippetRunner().run("print('live qa')\n")

    assert result.ok
    assert result.stdout.strip() == "live qa"


def test_runner_captures_runtime_errors():
    result = PythonSnippetRunner().run("raise ValueError('bad input')\n")

    assert not result.ok
    assert "ValueError" in result.stderr


def test_runner_respects_explicit_timeout_for_slow_snippets():
    result = PythonSnippetRunner().run(
        "import time\n"
        "time.sleep(2.2)\n"
        "print('finished')\n",
        timeout=3.0,
    )

    assert result.ok
    assert "finished" in result.stdout
