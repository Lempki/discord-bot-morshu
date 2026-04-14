import asyncio
import io
import os
import tempfile
import discord
from discord import app_commands
from discord.ext import commands
from utils.checks import in_bot_channel
from utils.logging import log
from morshutalk import Morshu
from morshutalk.morshu import _ensure_loaded


class MorshuCog(commands.Cog, name="Morshu"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def _generate_audio(self, text: str) -> bytes:
        """CPU-bound; always call via run_in_executor. Returns WAV bytes."""
        segment = Morshu().load_text(text)
        if segment is False or len(segment) == 0:
            return b""
        buf = io.BytesIO()
        segment.export(buf, format="wav")
        return buf.getvalue()

    async def _followup(self, interaction: discord.Interaction, template: str, **kwargs) -> bool:
        """Send a followup if the template is non-empty. Returns True if sent."""
        if not (msg := template.format(**kwargs) if kwargs else template):
            return False
        await interaction.followup.send(msg)
        return True

    @app_commands.command(name="generate")
    @in_bot_channel()
    async def tts(self, interaction: discord.Interaction, text: str):
        """Generate a Morshu TTS WAV and send as a file attachment."""
        await interaction.response.defer()
        s = self.bot.strings
        replied = await self._followup(interaction, s.morshu_generating)

        loop = asyncio.get_running_loop()
        wav_bytes = await loop.run_in_executor(None, self._generate_audio, text)

        if not wav_bytes:
            if not await self._followup(interaction, s.morshu_empty) and not replied:
                await interaction.delete_original_response()
            return

        await interaction.followup.send(file=discord.File(io.BytesIO(wav_bytes), filename="morshu.wav"))
        log(f"[MorshuCog] sent TTS file for '{text[:40]}'")

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

        loop = asyncio.get_running_loop()
        wav_bytes = await loop.run_in_executor(None, self._generate_audio, text)

        if not wav_bytes:
            if not await self._followup(interaction, s.morshu_empty) and not replied:
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
        tmp.write(wav_bytes)
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
                await interaction.response.send_message(
                    "This command can only be used in the designated bot channel.",
                    ephemeral=True,
                )
            return
        raise error

    @commands.Cog.listener()
    async def on_ready(self):
        # Preload the g2p model and source WAV in a background thread so the
        # first /generate / /morshu command doesn't stall waiting for NLTK data.
        asyncio.get_running_loop().run_in_executor(None, _ensure_loaded)
        print(f"[{self.__class__.__name__}] loaded.")


async def setup(bot: commands.Bot):
    await bot.add_cog(MorshuCog(bot))
