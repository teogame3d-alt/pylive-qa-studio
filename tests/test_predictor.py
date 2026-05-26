from pathlib import Path

from pylive_qa_studio.core.predictor import ConceptPredictor


def test_predictor_detects_dataframe_and_chart_workflow():
    source = """
import pandas as pd
import seaborn as sns
df = pd.read_csv("data/sales.csv")
sns.barplot(data=df, x="month", y="value")
"""

    predictions = ConceptPredictor().predict(source)
    preview_types = {item.preview_type for item in predictions}

    assert "table-preview" in preview_types
    assert "chart-preview" in preview_types


def test_predictor_detects_ui_and_style_workflow():
    source = "from PyQt6.QtWidgets import QWidget\nwidget = QWidget()\n"

    predictions = ConceptPredictor().predict(source, open_files=[Path("style.py")])
    preview_types = {item.preview_type for item in predictions}

    assert "ui-preview" in preview_types
    assert "style-preview" in preview_types

