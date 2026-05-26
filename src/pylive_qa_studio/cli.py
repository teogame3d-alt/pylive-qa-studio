"""Terminal interface for the live QA analyzer."""

from __future__ import annotations

import argparse
from pathlib import Path

from pylive_qa_studio.core.analyzer import LiveCodeAnalyzer
from pylive_qa_studio.core.predictor import ConceptPredictor


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI parser used by the package entry point."""

    parser = argparse.ArgumentParser(
        prog="pylive-qa",
        description="Analyze a Python file and print QA-oriented feedback.",
    )
    parser.add_argument("path", type=Path, help="Python file to analyze")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run file analysis from the command line."""

    args = build_parser().parse_args(argv)
    source = args.path.read_text(encoding="utf-8")

    analyzer = LiveCodeAnalyzer()
    predictor = ConceptPredictor()

    diagnostics = analyzer.analyze(source, filename=str(args.path))
    predictions = predictor.predict(source, open_files=[args.path])

    print(f"Analysis for {args.path}")
    print("=" * 72)

    if diagnostics:
        print("\nDiagnostics")
        for diagnostic in diagnostics:
            print(f"- L{diagnostic.line} [{diagnostic.severity}] {diagnostic.code}: {diagnostic.message}")
            print(f"  Suggestion: {diagnostic.suggestion}")
    else:
        print("\nDiagnostics: no issues detected by current MVP rules.")

    if predictions:
        print("\nConcept Predictions")
        for prediction in predictions:
            print(f"- {prediction.preview_type}: {prediction.reason}")
            print(f"  Next step: {prediction.suggested_next_step}")

    return 1 if any(item.severity == "error" for item in diagnostics) else 0

