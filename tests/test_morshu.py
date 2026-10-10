"""Tests for how /generate delivers its file when Discord drops the connection."""

from unittest.mock import AsyncMock, MagicMock

import aiohttp
import discord
import pytest

from cogs.morshu import _reply_with_file
from tests.conftest import make_interaction

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

    assert await _reply_with_file(interaction, b"RIFF", "morshu.wav")

    kwargs = interaction.edit_original_response.await_args.kwargs
    assert kwargs["content"] is None
    assert [file.filename for file in kwargs["attachments"]] == ["morshu.wav"]
    interaction.followup.send.assert_not_awaited()


async def test_dropped_connection_is_retried() -> None:
    interaction = interaction_whose_edits(DISCONNECTED, None)

    assert await _reply_with_file(interaction, b"RIFF", "morshu.wav")
    assert interaction.edit_original_response.await_count == 2


@pytest.mark.parametrize(
    ("stored", "delivered"), [(("morshu.mp4",), True), ((), False)]
)
async def test_discord_decides_after_every_attempt_fails(
    stored: tuple[str, ...], delivered: bool
) -> None:
    interaction = interaction_whose_edits(DISCONNECTED, DISCONNECTED, DISCONNECTED)
    interaction.original_response = AsyncMock(return_value=reply_with(*stored))

    assert await _reply_with_file(interaction, b"mp4", "morshu.mp4") is delivered
    assert interaction.edit_original_response.await_count == 3


async def test_unreachable_discord_counts_as_not_delivered() -> None:
    interaction = interaction_whose_edits(DISCONNECTED, DISCONNECTED, DISCONNECTED)
    interaction.original_response = AsyncMock(
        side_effect=discord.HTTPException(
            MagicMock(status=503, reason="Unavailable"), ""
        )
    )

    assert not await _reply_with_file(interaction, b"RIFF", "morshu.wav")
