import logging

from pydantic import ValidationError

from .llm import json_call
from .schemas import Report

logger = logging.getLogger(__name__)

SYSTEM = """You are a tech research synthesizer. You receive a topic and a list of retrieved sources.

Rules:
- Use ONLY the provided items. Do not use outside knowledge.
- Cite sources by numeric `id` only (the [id] at the start of each line).
- Never output URLs. Never invent source IDs.
- Every trend and learn entry needs at least one `source_id`.
- Roadmap weeks reference `resource_ids` chosen from the provided item ids (may be empty).
- Return JSON only matching this schema:
{
  "trends": [{"title": str, "why_now": str, "source_ids": [int, ...]} (3-6 items)],
  "learn": [{"skill": str, "why": str, "source_ids": [int, ...]} (3-5 items)],
  "roadmap": [{"week": int, "goal": str, "tasks": [str x1-5], "resource_ids": [int, ...]} (3-4 items)]
}"""


def _compact(items) -> str:
    lines = []
    for it in items:
        if isinstance(it, dict):
            _id = it.get("id")
            title = it.get("title", "")
            domain = it.get("domain", "")
            date = it.get("published_at", "")
            snippet = (it.get("snippet", "") or "")[:300]
        else:
            _id = getattr(it, "id", None)
            title = getattr(it, "title", "")
            domain = getattr(it, "domain", "")
            date = getattr(it, "published_at", "") or ""
            snippet = (getattr(it, "snippet", "") or "")[:300]
        lines.append(f"[{_id}] {title} | {domain} | {date} | {snippet}")
    return "\n".join(lines)


def synthesize(topic: str, items) -> dict:
    """Pure function: build a validated report dict from topic + items."""
    user = f"Topic: {topic}\nSources:\n{_compact(items)}"
    try:
        data = json_call(SYSTEM, user)
        return Report.model_validate(data).model_dump()
    except (ValidationError, Exception) as e:
        logger.warning("synthesize first attempt failed: %s", e)
        retry_user = user + f"\n\nPrevious output failed validation: {e}\nFix it and return valid JSON only."
        data = json_call(SYSTEM, retry_user)
        try:
            return Report.model_validate(data).model_dump()
        except ValidationError:
            logger.exception("synthesize retry failed")
            raise
