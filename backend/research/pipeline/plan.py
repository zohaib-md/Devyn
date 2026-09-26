import datetime
import logging

from .llm import json_call

logger = logging.getLogger(__name__)


def plan_queries(topic: str) -> list[str]:
    """Ask the LLM for 4-6 search queries covering news, tools, discussion, learning."""
    now = datetime.datetime.now(datetime.timezone.utc)
    month_year = now.strftime("%B %Y")
    system = (
        "You are a research planner. Return JSON only with the shape "
        '{"queries": ["..."]}. Produce 4-6 search queries about the topic. '
        "They must cover: recent news/releases, new tools or libraries, "
        "developer discussion, and learning resources."
    )
    user = f"Topic: {topic}\nCurrent month and year: {month_year}\nTarget recent content."
    try:
        data = json_call(system, user)
        queries = data.get("queries", [])
        if isinstance(queries, list):
            cleaned = [q.strip() for q in queries if isinstance(q, str) and q.strip()]
            if 1 <= len(cleaned) <= 10:
                return cleaned[:6] if len(cleaned) > 6 else cleaned
            if len(cleaned) >= 4:
                return cleaned[:6]
        return [topic]
    except Exception:
        logger.exception("plan_queries failed, falling back to [topic]")
        return [topic]
