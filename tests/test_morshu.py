"""Tests for how /generate delivers its file when Discord drops the connection."""

from unittest.mock import AsyncMock, MagicMock

import aiohttp
import discord
import pytest

from cogs.morshu import _caption, _reply_with_caption, _reply_with_file
from tests.conftest import make_interaction
from utils.replies import finish

DISCONNECTED = aiohttp.ServerDisconnectedError("Server disconnected")


def reply_with(*filenames: str) -> MagicMock:
    """A message whose attachments carry the given file names."""
    attachments = []
    for name in filenames:
        attachment = MagicMock()
        attachment.filename = name
        attachments.append(attachment)
    return MagicMock(attachments=attachments)


def interaction_whose_edits(*outcomes: object) -> MagicMock:
    """An interaction whose reply edits succeed or raise in the given order."""
    interaction = make_interaction(deferred=True)
    interaction.edit_original_response = AsyncMock(side_effect=list(outcomes))
    interaction.original_response = AsyncMock(return_value=reply_with())
    return interaction


async def test_file_replaces_the_reply() -> None:
    interaction = interaction_whose_edits(None)

    assert await _reply_with_file(interaction, b"RIFF", "morshu.wav", "> hi")

    kwargs = interaction.edit_original_response.await_args.kwargs
    assert kwargs["content"] == "> hi"
    mentions = kwargs["allowed_mentions"]
    assert not (mentions.everyone or mentions.users or mentions.roles)
    assert [file.filename for file in kwargs["attachments"]] == ["morshu.wav"]
    interaction.followup.send.assert_not_awaited()


async def test_dropped_connection_is_retried() -> None:
    interaction = interaction_whose_edits(DISCONNECTED, None)

    assert await _reply_with_file(interaction, b"RIFF", "morshu.wav", "> hi")
    assert interaction.edit_original_response.await_count == 2


@pytest.mark.parametrize(
    ("stored", "delivered"), [(("morshu.mp4",), True), ((), False)]
)
async def test_discord_decides_after_every_attempt_fails(
    stored: tuple[str, ...], delivered: bool
) -> None:
    interaction = interaction_whose_edits(DISCONNECTED, DISCONNECTED, DISCONNECTED)
    interaction.original_response = AsyncMock(return_value=reply_with(*stored))

    assert (
        await _reply_with_file(interaction, b"mp4", "morshu.mp4", "> hi") is delivered
    )
    assert interaction.edit_original_response.await_count == 3


async def test_unreachable_discord_counts_as_not_delivered() -> None:
    interaction = interaction_whose_edits(DISCONNECTED, DISCONNECTED, DISCONNECTED)
    interaction.original_response = AsyncMock(
        side_effect=discord.HTTPException(
            MagicMock(status=503, reason="Unavailable"), ""
        )
    )

    assert not await _reply_with_file(interaction, b"RIFF", "morshu.wav", "> hi")


@pytest.mark.parametrize(
    ("text", "caption"),
    [
        ("Lamp oil, rope, bombs", "> Lamp oil, rope, bombs"),
        ("||hidden||", r"> \|\|hidden\|\|"),
        ("# huge", r"> \# huge"),
        ("[click](https://x.y)", r"> \[click](https://x.y)"),
        ("@everyone listen", "> @everyone listen"),
    ],
    ids=["plain", "spoiler", "heading", "masked-link", "mention"],
)
def test_caption_shows_the_text_exactly_as_typed(text: str, caption: str) -> None:
    assert _caption(text) == caption


async def test_voice_caption_replaces_the_reply_and_stays() -> None:
    interaction = interaction_whose_edits(None)

    await _reply_with_caption(interaction, "> Lamp oil")
    await finish(interaction)

    kwargs = interaction.edit_original_response.await_args.kwargs
    assert kwargs["content"] == "> Lamp oil"
    mentions = kwargs["allowed_mentions"]
    assert not (mentions.everyone or mentions.users or mentions.roles)
    interaction.delete_original_response.assert_not_awaited()


async def test_failed_voice_caption_does_not_stop_the_command() -> None:
    interaction = interaction_whose_edits(DISCONNECTED)

    await _reply_with_caption(interaction, "> Lamp oil")
    await finish(interaction)

    # Without a caption, nothing replied, so the "is thinking..." message is cleaned up.
    interaction.delete_original_response.assert_awaited_once()
