"""Tests for research.pipeline.validate (pure function, no DB)."""
from research.pipeline.validate import validate


def _items():
    return [{"id": 1}, {"id": 2}, {"id": 3}]


def test_unknown_ids_removed():
    report = {
        "trends": [{"title": "T", "why_now": "W", "source_ids": [1, 99]}],
        "learn": [{"skill": "S", "why": "W", "source_ids": [2]}],
        "roadmap": [{"week": 1, "goal": "G", "tasks": ["a"], "resource_ids": [3, 100]}],
    }
    out = validate(report, _items())
    assert out["trends"][0]["source_ids"] == [1]
    assert out["roadmap"][0]["resource_ids"] == [3]
    # 99 and 100 dropped = 2
    assert out["meta"] == {"dropped_citations": 2, "item_count": 3}


def test_entries_with_no_sources_dropped():
    report = {
        "trends": [
            {"title": "Bad", "why_now": "x", "source_ids": [999]},
            {"title": "Good", "why_now": "y", "source_ids": [1]},
        ],
        "learn": [{"skill": "Gone", "why": "z", "source_ids": [888]}],
        "roadmap": [{"week": 1, "goal": "G", "tasks": ["a"], "resource_ids": []}],
    }
    out = validate(report, _items())
    assert len(out["trends"]) == 1
    assert out["trends"][0]["title"] == "Good"
    assert out["learn"] == []
    # roadmap weeks survive with filtered resources
    assert len(out["roadmap"]) == 1
    assert out["roadmap"][0]["resource_ids"] == []
    assert out["meta"]["dropped_citations"] == 2
    assert out["meta"]["item_count"] == 3


def test_roadmap_weeks_survive_with_filtered_resources():
    report = {
        "trends": [{"title": "T", "why_now": "W", "source_ids": [1]}],
        "learn": [{"skill": "S", "why": "W", "source_ids": [2]}],
        "roadmap": [
            {"week": 1, "goal": "G1", "tasks": ["a"], "resource_ids": [1, 999]},
            {"week": 2, "goal": "G2", "tasks": ["b"], "resource_ids": [777]},
        ],
    }
    out = validate(report, _items())
    assert len(out["roadmap"]) == 2
    assert out["roadmap"][0]["resource_ids"] == [1]
    assert out["roadmap"][1]["resource_ids"] == []
    assert out["meta"]["dropped_citations"] == 2
