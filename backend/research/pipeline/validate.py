"""Pure validation: strip citations that don't exist in items."""


def validate(report: dict, items) -> dict:
    valid_ids = {item["id"] if isinstance(item, dict) else item.id for item in items}
    dropped = 0

    def _filter(ids: list) -> list[int]:
        nonlocal dropped
        kept = []
        for i in ids or []:
            if i in valid_ids:
                kept.append(i)
            else:
                dropped += 1
        return kept

    trends = []
    for t in report.get("trends", []):
        sids = _filter(t.get("source_ids", []))
        if sids:
            trends.append({**t, "source_ids": sids})

    learn = []
    for item in report.get("learn", []):
        sids = _filter(item.get("source_ids", []))
        if sids:
            learn.append({**item, "source_ids": sids})

    roadmap = []
    for week in report.get("roadmap", []):
        rids = _filter(week.get("resource_ids", []))
        roadmap.append({**week, "resource_ids": rids})

    out = {**report, "trends": trends, "learn": learn, "roadmap": roadmap}
    out["meta"] = {"dropped_citations": dropped, "item_count": len(items)}
    return out
