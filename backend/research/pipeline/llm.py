import json
import logging

from django.conf import settings
from openai import OpenAI

logger = logging.getLogger(__name__)


def json_call(system: str, user: str) -> dict:
    """Call DeepSeek (OpenAI-compatible) in JSON mode and return parsed dict."""
    client = OpenAI(
        api_key=settings.DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com",
        timeout=60.0,
    )
    response = client.chat.completions.create(
        model=settings.DEEPSEEK_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content or "{}"
    return json.loads(content)
