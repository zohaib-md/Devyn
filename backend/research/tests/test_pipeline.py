"""Pipeline test: synthesize -> validate against recorded fixtures, no network."""
import json
from pathlib import Path
from unittest.mock import patch

from research.pipeline.schemas import Report
from research.pipeline.synthesize import synthesize
from research.pipeline.validate import validate

FIXTURE = Path(__file__).parent / "fixtures" / "items.json"

CANNED = {
    "trends": [
        {"title": "On-device AI toolkits", "why_now": "New releases this month", "source_ids": [1, 3]},
        {"title": "Kotlin AI libraries", "why_now": "Community momentum", "source_ids": [2]},
        {"title": "Curated sample repos", "why_now": "Stars spiking", "source_ids": [4, 99]},
    ],
    "learn": [
        {"skill": "ML Kit", "why": "Covers common use cases", "source_ids": [5]},
        {"skill": "Gemini Nano", "why": "On-device inference", "source_ids": [1]},
        {"skill": "Ghost skill", "why": "Should be dropped", "source_ids": [999]},
    ],
    "roadmap": [
        {"week": 1, "goal": "Foundations", "tasks": ["Set up Android Studio", "Run ML Kit sample"], "resource_ids": [5]},
        {"week": 2, "goal": "On-device inference", "tasks": ["Try Gemini Nano sample"], "resource_ids": [1, 1000]},
        {"week": 3, "goal": "Ship a mini app", "tasks": ["Build and polish"], "resource_ids": []},
    ],
}


def test_synthesize_validate_with_fixture():
    items = json.loads(FIXTURE.read_text())
    with patch("research.pipeline.synthesize.json_call", return_value=CANNED):
        report = synthesize("Android + AI", items)
    # synthesize output must itself be a valid Report (id 99/999 pass pydantic, fail validate)
    Report.model_validate({k: v for k, v in report.items() if k in ("trends", "learn", "roadmap")})
    out = validate(report, items)
    assert len(out["trends"]) == 3
    assert out["trends"][2]["source_ids"] == [4]  # 99 dropped
    assert all(l["skill"] != "Ghost skill" for l in out["learn"])
    assert len(out["roadmap"]) == 3
    assert out["meta"]["item_count"] == 5
    assert out["meta"]["dropped_citations"] == 3  # 99, 999, 1000
