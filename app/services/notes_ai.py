"""AI-powered note connection suggestions."""
import json
import os

from google import genai
from google.genai.errors import APIError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.crud import get_candidate_notes
from app.schemas.notes_ai import (
    ConnectionSuggestion,
    SuggestionsSchema,
)

logger = get_logger(__name__)

#  Configuration
MODEL = "gemini-3-flash-preview"
MAX_CANDIDATES = 40
MAX_SUGGESTIONS = 5
MAX_OUTPUT_TOKENS = 500
TEMPERATURE = 0.2

#  Client (lazy, cached)

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            logger.error("gemini_api_key_missing")
            raise RuntimeError("GEMINI_API_KEY is not set")

        _client = genai.Client(api_key=api_key)

    return _client



async def suggest_connections(
    db: AsyncSession,
    user_id: int,
    title: str,
    content: str,
    exclude_note_id: int | None = None,
) -> SuggestionsSchema:
    """
    Suggest connections for a note (draft or existing).

    - Fetches candidate notes from the DB.
    - Builds a prompt.
    - Calls Gemini.
    - Filters out hallucinations and dedupes.
    """
    candidates = await get_candidate_notes(
        db=db,
        user_id=user_id,
        exclude_note_id=exclude_note_id,
        limit=MAX_CANDIDATES,
    )

    if not candidates:
        return SuggestionsSchema(connections=[])

    prompt = _build_prompt(title, content, candidates)

    try:
        raw = await _call_ai(prompt)
    except RuntimeError:
        # AI failure → don't break the request; return no suggestions.
        return SuggestionsSchema(connections=[])

    known = {c.title.strip().lower() for c in candidates}
    seen: set[str] = set()
    connections: list[ConnectionSuggestion] = []

    for item in raw:
        key = item.title.strip().lower()
        if key not in known or key in seen:
            continue

        seen.add(key)
        connections.append(item)

        if len(connections) >= MAX_SUGGESTIONS:
            break

    return SuggestionsSchema(connections=connections)



def _build_prompt(title: str, content: str, candidates: list) -> str:
    candidate_list = "\n".join(
        f"{i + 1}. {c.title}\n   {c.content[:240]}"
        for i, c in enumerate(candidates)
    )

    return "\n".join([
        "You help maintain a Zettelkasten note box.",
        "",
        "Task: given a NEW note, suggest which EXISTING notes it should link to.",
        "",
        "Rules (strict):",
        "1. Only suggest notes whose title appears EXACTLY in the existing notes list.",
        "2. Do not invent titles. Do not paraphrase titles.",
        f"3. Suggest at most {MAX_SUGGESTIONS} connections.",
        "4. Each reason must be ONE short sentence (max 20 words).",
        "5. Prefer conceptual overlap over keyword matching.",
        "6. If nothing is related, return an empty array.",
        "",
        "Output format (JSON, no markdown):",
        '{ "connections": [ { "title": "<exact title>", "reason": "<one sentence>" } ] }',
        "",
        "---",
        f"NEW NOTE TITLE: {title or '(untitled)'}",
        "",
        "NEW NOTE BODY:",
        content,
        "",
        "EXISTING NOTES:",
        candidate_list or "(none)",
    ])


async def _call_ai(prompt: str) -> list[ConnectionSuggestion]:
    """Call Gemini and parse the JSON output into validated objects."""
    client = _get_client()

    try:
        interaction = client.interactions.create(
            model=MODEL,
            input=prompt,
            generation_config={
                "temperature": TEMPERATURE,
                "max_output_tokens": MAX_OUTPUT_TOKENS,
                "thinking_level": "low",
            },
        )
    except APIError as exc:
        logger.exception(
            "gemini_suggestion_request_failed",
            model=MODEL,
        )
        raise RuntimeError(f"Gemini API error: {exc}") from exc

    raw_text = interaction.output_text
    if not raw_text:
        logger.warning(
            "gemini_suggestion_empty_response",
            model=MODEL,
        )
        return []

    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        # remove ```json ... ``` or ``` ... ```
        cleaned = cleaned.split("```")[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()

    try:
        payload = json.loads(cleaned)
    except json.JSONDecodeError:
        logger.warning(
            "gemini_suggestion_invalid_json",
            model=MODEL,
            response_length=len(raw_text),
        )
        return []

    connections: list[ConnectionSuggestion] = []
    for item in payload.get("connections", []):
        try:
            connections.append(
                ConnectionSuggestion(
                    title=item["title"],
                    reason=item["reason"],
                )
            )
        except (KeyError, TypeError, ValidationError):
            continue
    return connections
