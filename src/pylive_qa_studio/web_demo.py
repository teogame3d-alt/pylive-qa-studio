"""Local web demo for Python Live QA Studio.

The demo uses only the Python standard library so it can run in a fresh clone
without a framework dependency. The browser UI calls the same analyzer,
predictor, executor, and traceback explainer used by the CLI and tests.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from pylive_qa_studio.core.analyzer import LiveCodeAnalyzer
from pylive_qa_studio.core.error_explainer import TracebackExplainer
from pylive_qa_studio.core.execution_policy import ExecutionPolicy
from pylive_qa_studio.core.executor import PythonSnippetRunner
from pylive_qa_studio.core.predictor import ConceptPredictor

WEB_DIR = Path(__file__).resolve().parents[2] / "web"


def analyze_source(source: str) -> dict[str, Any]:
    """Return diagnostics and concept predictions for source code."""

    diagnostics = LiveCodeAnalyzer().analyze(source, filename="<live-editor>")
    predictions = ConceptPredictor().predict(source)
    return {
        "diagnostics": [asdict(item) for item in diagnostics],
        "predictions": [asdict(item) for item in predictions],
    }


def run_source(source: str) -> dict[str, Any]:
    """Run a snippet and explain the traceback when execution fails."""

    run_plan = ExecutionPolicy().plan(source)
    result = PythonSnippetRunner().run(source, timeout=run_plan.timeout_seconds)
    payload: dict[str, Any] = {
        "run_plan": asdict(run_plan),
        "execution": asdict(result),
    }
    if result.stderr:
        payload["runtime_diagnostic"] = asdict(TracebackExplainer().explain(result.stderr))
    return payload


class DemoRequestHandler(SimpleHTTPRequestHandler):
    """HTTP handler for the local demo UI and JSON endpoints."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)

    def do_POST(self) -> None:
        """Handle JSON API requests from the browser demo."""

        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8")
        data = json.loads(body or "{}")
        source = str(data.get("source", ""))

        if self.path == "/api/analyze":
            self._write_json(analyze_source(source))
            return
        if self.path == "/api/run":
            self._write_json(run_source(source))
            return

        self.send_error(404, "Unknown API route")

    def _write_json(self, payload: dict[str, Any]) -> None:
        encoded = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


def main(argv: list[str] | None = None) -> int:
    """Start the local browser demo."""

    argv = argv or []
    port = int(argv[0]) if argv else 8765
    server = ThreadingHTTPServer(("localhost", port), DemoRequestHandler)
    print(f"Python Live QA Studio demo running at http://localhost:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping demo server.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
