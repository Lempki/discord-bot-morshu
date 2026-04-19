import io
import os
import tempfile

import discord
import httpx
from discord import app_commands
from discord.ext import commands

from utils.checks import in_bot_channel
from utils.logging import log


class MorshuCog(commands.Cog, name="Morshu"):
    def __init__(self, bot: commands.Bot):
        if not bot.config.DISCORD_API_TTS_URL or not bot.config.DISCORD_API_TTS_SECRET:
            raise RuntimeError(
                "DISCORD_API_TTS_URL and DISCORD_API_TTS_SECRET must be set to use the morshu cog."
            )
        self.bot = bot
        self._http = httpx.AsyncClient(
            base_url=bot.config.DISCORD_API_TTS_URL,
            headers={"Authorization": f"Bearer {bot.config.DISCORD_API_TTS_SECRET}"},
            timeout=60.0,
        )

    async def cog_unload(self) -> None:
        await self._http.aclose()

    async def _call_api(self, text: str, fmt: str = "wav") -> bytes:
        resp = await self._http.post("/tts/synthesize", json={"text": text, "format": fmt})
        resp.raise_for_status()
        return resp.content

    async def _followup(self, interaction: discord.Interaction, template: str, **kwargs) -> bool:
        if not (msg := template.format(**kwargs) if kwargs else template):
            return False
        await interaction.followup.send(msg)
        return True

    @app_commands.command(name="generate")
    @app_commands.describe(format="Output format", text="Text to synthesize")
    @app_commands.choices(format=[
        app_commands.Choice(name="WAV audio", value="wav"),
        app_commands.Choice(name="MP4 video", value="video"),
    ])
    @in_bot_channel()
    async def tts(
        self,
        interaction: discord.Interaction,
        format: app_commands.Choice[str],
        text: str,
    ):
        """Generate Morshu TTS and send as a file attachment."""
        await interaction.response.defer()
        s = self.bot.strings
        fmt = format.value

        replied = await self._followup(interaction, s.morshu_generating)

        try:
            data = await self._call_api(text, fmt)
        except Exception as exc:
            log(f"[MorshuCog] synthesis error: {exc}")
            if not await self._followup(interaction, s.morshu_empty) and not replied:
                await interaction.delete_original_response()
            return

        if not data:
            if not await self._followup(interaction, s.morshu_empty) and not replied:
                await interaction.delete_original_response()
            return

        filename = "morshu.mp4" if fmt == "video" else "morshu.wav"
        await interaction.followup.send(file=discord.File(io.BytesIO(data), filename=filename))
        log(f"[MorshuCog] sent TTS {fmt} for '{text[:40]}'")

    @app_commands.command(name="morshu")
    @in_bot_channel()
    async def speak(self, interaction: discord.Interaction, text: str):
        """Join the user's voice channel and play Morshu TTS audio."""
        await interaction.response.defer()
        s = self.bot.strings
        replied = False

        if interaction.user.voice is None:
            replied = await self._followup(interaction, s.not_in_voice, user=interaction.user)
            if not replied:
                await interaction.delete_original_response()
            return

        replied = await self._followup(interaction, s.morshu_generating)

        try:
            data = await self._call_api(text, "wav")
        except Exception as exc:
            log(f"[MorshuCog] synthesis error: {exc}")
            if not await self._followup(interaction, s.morshu_empty) and not replied:
                await interaction.delete_original_response()
            return

        if not data:
            if not await self._followup(interaction, s.morshu_empty) and not replied:
                await interaction.delete_original_response()
            return

        if interaction.user.voice is None:
            replied = await self._followup(interaction, s.not_in_voice, user=interaction.user) or replied
            if not replied:
                await interaction.delete_original_response()
            return

        target = interaction.user.voice.channel
        vc = interaction.guild.voice_client
        if vc is None:
            vc = await target.connect()
            replied = await self._followup(interaction, s.joined_voice, channel=target) or replied
        elif vc.channel != target:
            await vc.move_to(target)
            replied = await self._followup(interaction, s.moved_voice, channel=target) or replied

        if vc.is_playing():
            vc.stop()

        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        tmp.write(data)
        tmp.close()
        tmp_path = tmp.name

        def after_playback(error):
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            if error:
                log(f"[MorshuCog] playback error: {error}")

        ffmpeg = self.bot.config.FFMPEG_PATH or "ffmpeg"
        vc.play(
            discord.FFmpegPCMAudio(source=tmp_path, executable=ffmpeg),
            after=after_playback,
        )
        log(f"[MorshuCog] playing TTS in '{target.name}' for '{text[:40]}'")
        if not replied:
            await interaction.delete_original_response()

    async def cog_app_command_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        if isinstance(error, app_commands.CheckFailure):
            if not interaction.response.is_done():
                if msg := self.bot.strings.bot_channel_only:
                    await interaction.response.send_message(msg, ephemeral=True)
            return
        raise error

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"[{self.__class__.__name__}] loaded.")


async def setup(bot: commands.Bot):
    await bot.add_cog(MorshuCog(bot))
