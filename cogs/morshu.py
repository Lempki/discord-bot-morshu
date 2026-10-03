"""Morshu speech through discord-api-morshu, sent as a file or spoken in a voice channel."""

import io
import logging
from typing import TYPE_CHECKING

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
        """Closes the HTTP client of discord-api-morshu."""
        await self._http.aclose()

    async def _synthesize(self, text: str, output: str) -> bytes:
        """Asks discord-api-morshu to speak a text.

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
        await interaction.followup.send(
            file=discord.File(io.BytesIO(data), filename=filename)
        )
        # The file is the reply, so finish() must never delete it.
        mark_replied(interaction)
        log.info(f"Sent a {output.value} file for '{text[:40]}' in {guild}.")

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
