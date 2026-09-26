"""Tests for app.services.notes_ai."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models import Note, NoteType
from app.schemas.notes_ai import ConnectionSuggestion, SuggestionsSchema
from app.services import notes_ai
from app.services.notes_ai import (
    _build_prompt,
    _call_ai,
    suggest_connections,
)



def make_note(note_id: int, title: str, content: str = "some content") -> Note:
    """Build a transient Note object (not persisted)."""
    n = Note(
        title=title,
        content=content,
        note_type=NoteType.PERMANENT,
        user_id=1,
    )
    n.id = note_id
    return n


def make_interaction(text: str) -> MagicMock:
    """Mock a google-genai Interaction with .output_text."""
    interaction = MagicMock()
    interaction.output_text = text
    return interaction




class TestBuildPrompt:
    def test_includes_title_and_content(self):
        candidates = [make_note(1, "Alpha"), make_note(2, "Beta")]
        prompt = _build_prompt("New note", "New body", candidates)

        assert "NEW NOTE TITLE: New note" in prompt
        assert "NEW NOTE BODY:" in prompt
        assert "New body" in prompt
        assert "1. Alpha" in prompt
        assert "2. Beta" in prompt

    def test_handles_empty_title(self):
        prompt = _build_prompt("", "body", [])
        assert "NEW NOTE TITLE: (untitled)" in prompt

    def test_handles_empty_candidates(self):
        prompt = _build_prompt("Title", "body", [])
        assert "EXISTING NOTES:\n(none)" in prompt

    def test_truncates_long_candidate_content(self):
        long_content = "x" * 500
        candidates = [make_note(1, "Alpha", long_content)]
        prompt = _build_prompt("T", "b", candidates)

        # Only the first 240 chars of the candidate body are used
        assert "x" * 240 in prompt
        assert "x" * 241 not in prompt




class TestCallAi:
    @pytest.mark.asyncio
    async def test_parses_valid_json(self):
        payload = (
            '{"connections": ['
            '{"title": "Alpha", "reason": "Same idea"},'
            '{"title": "Beta", "reason": "Related concept"}'
            "]}"
        )
        interaction = make_interaction(payload)

        with patch.object(notes_ai, "_get_client") as mock_get:
            mock_get.return_value.interactions.create.return_value = interaction
            result = await _call_ai("prompt")

        assert len(result) == 2
        assert result[0] == ConnectionSuggestion(title="Alpha", reason="Same idea")
        assert result[1].title == "Beta"

    @pytest.mark.asyncio
    async def test_strips_markdown_fences(self):
        payload = (
            "```json\n"
            '{"connections": [{"title": "Alpha", "reason": "x"}]}\n'
            "```"
        )
        interaction = make_interaction(payload)

        with patch.object(notes_ai, "_get_client") as mock_get:
            mock_get.return_value.interactions.create.return_value = interaction
            result = await _call_ai("prompt")

        assert len(result) == 1
        assert result[0].title == "Alpha"

    @pytest.mark.asyncio
    async def test_invalid_json_returns_empty(self):
        interaction = make_interaction("this is not json at all")

        with patch.object(notes_ai, "_get_client") as mock_get:
            mock_get.return_value.interactions.create.return_value = interaction
            result = await _call_ai("prompt")

        assert result == []

    @pytest.mark.asyncio
    async def test_empty_output_returns_empty(self):
        interaction = make_interaction("")

        with patch.object(notes_ai, "_get_client") as mock_get:
            mock_get.return_value.interactions.create.return_value = interaction
            result = await _call_ai("prompt")

        assert result == []

    @pytest.mark.asyncio
    async def test_skips_malformed_connection_items(self):
        payload = (
            '{"connections": ['
            '{"title": "Alpha", "reason": "ok"},'
            '{"title": "Beta"},'                     # missing reason
            '{"reason": "no title"},'                # missing title
            '"just a string",'                       # not a dict
            '{"title": "Gamma", "reason": "fine"}'
            "]}"
        )
        interaction = make_interaction(payload)

        with patch.object(notes_ai, "_get_client") as mock_get:
            mock_get.return_value.interactions.create.return_value = interaction
            result = await _call_ai("prompt")

        assert [c.title for c in result] == ["Alpha", "Gamma"]

    @pytest.mark.asyncio
    async def test_api_error_raises_runtime_error(self):
        class FakeAPIError(Exception):
            pass

        with (
            patch.object(notes_ai, "APIError", FakeAPIError),
            patch.object(notes_ai, "_get_client") as mock_get,
        ):
            mock_get.return_value.interactions.create.side_effect = FakeAPIError(
                "boom"
            )
            with pytest.raises(RuntimeError, match="Gemini API error"):
                await _call_ai("prompt")



class TestSuggestConnections:
    @pytest.mark.asyncio
    async def test_no_candidates_skips_ai(self):
        """When the user has no other notes, the AI is never called."""
        with (
            patch.object(
                notes_ai, "get_candidate_notes", new=AsyncMock(return_value=[])
            ) as mock_candidates,
            patch.object(notes_ai, "_call_ai", new=AsyncMock()) as mock_ai,
        ):
            result = await suggest_connections(
                db=MagicMock(),
                user_id=1,
                title="T",
                content="some content",
            )

        assert result.connections == []
        mock_candidates.assert_awaited_once()
        mock_ai.assert_not_called()

    @pytest.mark.asyncio
    async def test_returns_filtered_suggestions(self):
        candidates = [
            make_note(1, "Alpha"),
            make_note(2, "Beta"),
            make_note(3, "Gamma"),
        ]
        ai_output = [
            ConnectionSuggestion(title="Alpha", reason="related"),
            ConnectionSuggestion(title="Beta", reason="also related"),
        ]

        with (
            patch.object(
                notes_ai,
                "get_candidate_notes",
                new=AsyncMock(return_value=candidates),
            ),
            patch.object(notes_ai, "_call_ai", new=AsyncMock(return_value=ai_output)),
        ):
            result = await suggest_connections(
                db=MagicMock(),
                user_id=1,
                title="New",
                content="some content here",
            )

        assert len(result.connections) == 2
        assert {c.title for c in result.connections} == {"Alpha", "Beta"}

    @pytest.mark.asyncio
    async def test_filters_hallucinated_titles(self):
        """The AI invents 'Delta' — it must be dropped."""
        candidates = [make_note(1, "Alpha")]
        ai_output = [
            ConnectionSuggestion(title="Alpha", reason="ok"),
            ConnectionSuggestion(title="Delta", reason="invented"),
        ]

        with (
            patch.object(
                notes_ai,
                "get_candidate_notes",
                new=AsyncMock(return_value=candidates),
            ),
            patch.object(notes_ai, "_call_ai", new=AsyncMock(return_value=ai_output)),
        ):
            result = await suggest_connections(
                db=MagicMock(),
                user_id=1,
                title="New",
                content="some content here",
            )

        assert [c.title for c in result.connections] == ["Alpha"]

    @pytest.mark.asyncio
    async def test_dedupes_repeated_titles_case_insensitive(self):
        candidates = [make_note(1, "Alpha")]
        ai_output = [
            ConnectionSuggestion(title="Alpha", reason="first"),
            ConnectionSuggestion(title="alpha", reason="second"),
            ConnectionSuggestion(title="ALPHA", reason="third"),
        ]

        with (
            patch.object(
                notes_ai,
                "get_candidate_notes",
                new=AsyncMock(return_value=candidates),
            ),
            patch.object(notes_ai, "_call_ai", new=AsyncMock(return_value=ai_output)),
        ):
            result = await suggest_connections(
                db=MagicMock(),
                user_id=1,
                title="New",
                content="some content here",
            )

        assert len(result.connections) == 1
        assert result.connections[0].reason == "first"

    @pytest.mark.asyncio
    async def test_caps_at_max_suggestions(self):
        # Create 10 candidates, all matchable
        candidates = [make_note(i, f"Note {i}") for i in range(1, 11)]
        ai_output = [
            ConnectionSuggestion(title=f"Note {i}", reason="r") for i in range(1, 11)
        ]

        with (
            patch.object(
                notes_ai,
                "get_candidate_notes",
                new=AsyncMock(return_value=candidates),
            ),
            patch.object(notes_ai, "_call_ai", new=AsyncMock(return_value=ai_output)),
        ):
            result = await suggest_connections(
                db=MagicMock(),
                user_id=1,
                title="New",
                content="some content here",
            )

        assert len(result.connections) == notes_ai.MAX_SUGGESTIONS

    @pytest.mark.asyncio
    async def test_ai_failure_returns_empty_gracefully(self):
        """A Gemini failure must not break the request."""
        candidates = [make_note(1, "Alpha")]

        with (
            patch.object(
                notes_ai,
                "get_candidate_notes",
                new=AsyncMock(return_value=candidates),
            ),
            patch.object(
                notes_ai,
                "_call_ai",
                new=AsyncMock(side_effect=RuntimeError("Gemini API error: boom")),
            ),
        ):
            result = await suggest_connections(
                db=MagicMock(),
                user_id=1,
                title="New",
                content="some content here",
            )

        assert result.connections == []

    @pytest.mark.asyncio
    async def test_passes_exclude_note_id_to_crud(self):
        with (
            patch.object(
                notes_ai,
                "get_candidate_notes",
                new=AsyncMock(return_value=[]),
            ) as mock_candidates,
        ):
            await suggest_connections(
                db=MagicMock(),
                user_id=42,
                title="T",
                content="some content",
                exclude_note_id=99,
            )

        mock_candidates.assert_awaited_once()
        _, kwargs = mock_candidates.call_args
        assert kwargs["user_id"] == 42
        assert kwargs["exclude_note_id"] == 99
        assert kwargs["limit"] == notes_ai.MAX_CANDIDATES
