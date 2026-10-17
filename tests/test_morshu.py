"""Tests for /generate and /morshu: delivering the file, the caption, and failures."""

from unittest.mock import AsyncMock, MagicMock

import aiohttp
import discord
import pytest

from bot import BotApp
from cogs.morshu import (
    MorshuCog,
    _caption,
    _megabytes,
    _reply_with_caption,
    _reply_with_file,
)
from config import Config, ServiceConfig
from localization import LOCALES
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


EN = LOCALES["en"]


def morshu_cog(data: bytes) -> MorshuCog:
    """The cog in an English bot, with a fake api-morshu that answers data."""
    services = {"morshu": ServiceConfig("http://morshu:8000", "s" * 16)}
    bot = BotApp(Config(discord_token="t", locale="en", services=services))
    cog = MorshuCog(bot)
    cog._synthesize = AsyncMock(return_value=data)  # type: ignore[method-assign]
    return cog


def command_interaction(*, filesize_limit: int = 10_000_000) -> MagicMock:
    interaction = make_interaction()
    interaction.guild.filesize_limit = filesize_limit
    interaction.edit_original_response = AsyncMock()
    return interaction


@pytest.mark.parametrize("output", ["wav", "video"])
async def test_a_failed_generation_replaces_the_generating_message(output: str) -> None:
    cog = morshu_cog(b"")
    interaction = command_interaction()
    choice = discord.app_commands.Choice(name=output, value=output)

    await cog.generate.callback(cog, interaction, choice, "Lamp oil")  # type: ignore[arg-type]

    # The generating message became the failure, so no stale message stays in the channel.
    interaction.followup.send.assert_awaited_once_with(
        EN.morshu_generating, ephemeral=False
    )
    interaction.edit_original_response.assert_awaited_once_with(content=EN.morshu_empty)


async def test_a_file_too_large_replaces_the_generating_message() -> None:
    cog = morshu_cog(b"x" * 2048)
    interaction = command_interaction(filesize_limit=1024)
    choice = discord.app_commands.Choice(name="wav", value="wav")

    await cog.generate.callback(cog, interaction, choice, "Lamp oil")  # type: ignore[arg-type]

    content = interaction.edit_original_response.await_args.kwargs["content"]
    assert content == EN.morshu_too_large.format(size="0.0", limit="0.0")


async def test_a_failed_voice_generation_replaces_the_generating_message() -> None:
    cog = morshu_cog(b"")
    member = MagicMock(spec=discord.Member)
    member.voice = MagicMock(channel=MagicMock(spec=discord.VoiceChannel))
    interaction = command_interaction()
    interaction.user = member

    await cog.morshu.callback(cog, interaction, "Lamp oil")  # type: ignore[arg-type]

    interaction.edit_original_response.assert_awaited_once_with(content=EN.morshu_empty)


async def test_a_file_that_never_arrives_leaves_no_generating_message(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("cogs.morshu._reply_with_file", AsyncMock(return_value=False))
    cog = morshu_cog(b"RIFF")
    interaction = command_interaction()
    choice = discord.app_commands.Choice(name="wav", value="wav")

    await cog.generate.callback(cog, interaction, choice, "Lamp oil")  # type: ignore[arg-type]

    interaction.delete_original_response.assert_awaited_once()
    last = interaction.followup.send.await_args
    assert last.args == (EN.morshu_send_failed,)
    assert last.kwargs["ephemeral"] is True


def test_sizes_use_the_languages_decimal_point() -> None:
    assert _megabytes(8_650_000, LOCALES["en"].decimal_point) == "8.2"
    assert _megabytes(8_650_000, LOCALES["fi"].decimal_point) == "8,2"
