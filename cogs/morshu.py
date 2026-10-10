"""Morshu speech through api-morshu, sent as a file or spoken in a voice channel."""

import io
import logging
from typing import TYPE_CHECKING

import aiohttp
import discord
import httpx
from discord import app_commands
from discord.ext import commands

from utils.audio import bytes_source
from utils.checks import guild_of, in_bot_channel
from utils.replies import finish, mark_replied, respond

if TYPE_CHECKING:
    from bot import BotApp

log = logging.getLogger(__name__)

_MEGABYTE = 1024 * 1024


def _megabytes(size: int) -> float:
    """Returns a size in bytes as megabytes, rounded to one decimal."""
    return round(size / _MEGABYTE, 1)


# Discord sometimes closes the connection after it stored an upload, before it answers.
_UPLOAD_ATTEMPTS = 3


def _caption(text: str) -> str:
    """Quotes the text that a generated file speaks, to show above the file.

    Moderators and moderation bots can then see what was generated without opening the file.
    Escaping shows the text exactly as typed, so formatting such as spoilers cannot hide words.
    The caption has no wording of its own, so it shows even when LOCALE=silent mutes replies.
    """
    return f"> {discord.utils.escape_markdown(text)}"


async def _reply_with_caption(interaction: discord.Interaction, caption: str) -> None:
    """Replaces the "generating" message with the text that Morshu speaks in voice.

    Speech in a voice channel leaves no trace in the chat otherwise.
    A failed edit only costs the caption, so playback goes ahead and the failure is logged.
    """
    try:
        await interaction.edit_original_response(
            content=caption,
            # The caption repeats user input, which must never ping anyone.
            allowed_mentions=discord.AllowedMentions.none(),
        )
    except (discord.HTTPException, aiohttp.ClientError, TimeoutError) as error:
        log.warning(f"Could not show the text that Morshu speaks: {error}")
        return
    # The caption is the reply, so finish() must never delete it.
    mark_replied(interaction)


async def _reply_has_file(interaction: discord.Interaction, filename: str) -> bool:
    """Asks Discord whether the command's reply holds the file."""
    try:
        reply = await interaction.original_response()
    except (discord.HTTPException, aiohttp.ClientError, TimeoutError):
        return False
    return any(attachment.filename == filename for attachment in reply.attachments)


async def _reply_with_file(
    interaction: discord.Interaction, data: bytes, filename: str, caption: str
) -> bool:
    """Puts a file into the command's reply, in place of the "generating" message.

    A dropped connection is retried, because editing the reply again never posts a second file.
    When every attempt fails, Discord is asked whether the file arrived anyway.

    Args:
        interaction: The deferred interaction whose reply receives the file.
        data: The file contents.
        filename: The name the file gets in Discord.
        caption: The text shown above the file.

    Returns:
        Whether the reply holds the file.
    """
    for attempt in range(1, _UPLOAD_ATTEMPTS + 1):
        try:
            await interaction.edit_original_response(
                content=caption,
                # The caption repeats user input, which must never ping anyone.
                allowed_mentions=discord.AllowedMentions.none(),
                attachments=[discord.File(io.BytesIO(data), filename=filename)],
            )
        except (aiohttp.ClientConnectionError, TimeoutError) as error:
            log.warning(
                f"Attempt {attempt} to send {filename} lost the connection: {error}"
            )
            continue
        return True
    return await _reply_has_file(interaction, filename)


class MorshuCog(commands.Cog, name="Morshu"):
    """Morshu text-to-speech as WAV audio, lip-synced MP4 video, or live voice."""

    def __init__(self, bot: "BotApp") -> None:
        # Raises ConfigError with the missing variable names, which stops the bot at startup.
        service = bot.config.service("morshu")
        self.bot = bot
        self._http = httpx.AsyncClient(
            base_url=service.url,
            headers={"Authorization": f"Bearer {service.secret}"},
            timeout=60.0,
        )

    async def cog_unload(self) -> None:
        """Closes the HTTP client of api-morshu."""
        await self._http.aclose()

    async def _synthesize(self, text: str, output: str) -> bytes:
        """Asks api-morshu to speak a text.

        Args:
            text: What Morshu says.
            output: The file type, which is "wav" or "video".

        Returns:
            The generated file. It is empty when the service produced nothing.

        Raises:
            httpx.HTTPError: If the service is unreachable or rejects the request.
        """
        response = await self._http.post(
            "/tts/synthesize", json={"text": text, "format": output}
        )
        response.raise_for_status()
        return response.content

    @app_commands.command(name="generate")
    @app_commands.guild_only()
    @in_bot_channel()
    @app_commands.rename(output="format")
    @app_commands.describe(
        output="The file type to create.",
        text="What Morshu says, up to 500 characters.",
    )
    @app_commands.choices(
        output=[
            app_commands.Choice(name="WAV audio", value="wav"),
            app_commands.Choice(name="MP4 video", value="video"),
        ]
    )
    async def generate(
        self,
        interaction: discord.Interaction,
        output: app_commands.Choice[str],
        text: app_commands.Range[str, 1, 500],
    ) -> None:
        """Generate Morshu speech and send it as a file."""
        # Generating speech takes longer than the 3 seconds Discord allows for a reply.
        await interaction.response.defer()
        s = self.bot.strings_for(interaction)
        guild = guild_of(interaction)
        await respond(interaction, s.morshu_generating)

        try:
            data = await self._synthesize(text, output.value)
        except httpx.HTTPError as error:
            log.warning(f"Synthesis failed: {error}")
            data = b""
        if not data:
            await respond(interaction, s.morshu_empty)
            await finish(interaction)
            return

        limit = guild.filesize_limit
        if len(data) > limit:
            await respond(
                interaction,
                s.morshu_too_large,
                size=_megabytes(len(data)),
                limit=_megabytes(limit),
            )
            await finish(interaction)
            return

        filename = "morshu.mp4" if output.value == "video" else "morshu.wav"
        if await _reply_with_file(interaction, data, filename, _caption(text)):
            # The file is the reply, so finish() must never delete it.
            mark_replied(interaction)
            log.info(f"Sent a {output.value} file for '{text[:40]}' in {guild}.")
            return
        log.warning(f"The {output.value} file for '{text[:40]}' did not reach Discord.")
        private = self.bot.strings_for(interaction, private=True)
        await respond(interaction, private.morshu_send_failed, ephemeral=True)
        await finish(interaction)

    @app_commands.command(name="morshu")
    @app_commands.guild_only()
    @in_bot_channel()
    @app_commands.describe(text="What Morshu says, up to 500 characters.")
    async def morshu(
        self, interaction: discord.Interaction, text: app_commands.Range[str, 1, 500]
    ) -> None:
        """Join your voice channel and speak as Morshu."""
        await interaction.response.defer()
        s = self.bot.strings_for(interaction)
        guild = guild_of(interaction)
        member = interaction.user
        if (
            not isinstance(member, discord.Member)
            or member.voice is None
            or member.voice.channel is None
        ):
            await respond(interaction, s.not_in_voice, user=member.display_name)
            await finish(interaction)
            return
        channel = member.voice.channel
        await respond(interaction, s.morshu_generating)

        try:
            data = await self._synthesize(text, "wav")
        except httpx.HTTPError as error:
            log.warning(f"Synthesis failed: {error}")
            data = b""
        if not data:
            await respond(interaction, s.morshu_empty)
            await finish(interaction)
            return

        vc = await self.bot.voice_presence.connect(channel)
        if vc.is_playing():
            vc.stop()
        await _reply_with_caption(interaction, _caption(text))
        # Playback lasts longer than the interaction should stay open, so the command ends first.
        await finish(interaction)
        log.info(f"Speaking '{text[:40]}' in {channel.name} of {guild}.")
        try:
            await self.bot.voice_presence.play(
                vc, bytes_source(data, self.bot.config.ffmpeg_path)
            )
        except Exception as error:
            log.warning(f"Playback in {guild} failed: {error}")

    async def cog_load(self) -> None:
        """Logs that the cog is ready."""
        log.info(f"{self.qualified_name} cog loaded.")


async def setup(bot: "BotApp") -> None:
    """Adds the cog. discord.py calls this when the extension loads."""
    await bot.add_cog(MorshuCog(bot))
