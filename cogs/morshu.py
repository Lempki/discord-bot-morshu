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

    @app_commands.command(name="generate")
    @in_bot_channel()
    async def tts(self, interaction: discord.Interaction, text: str):
        """Generate a Morshu TTS WAV and send as a file attachment."""
        await interaction.response.defer()
        s = self.bot.strings
        if msg := s.morshu_generating:
            await interaction.followup.send(msg)

        loop = asyncio.get_running_loop()
        wav_bytes = await loop.run_in_executor(None, self._generate_audio, text)

        if not wav_bytes:
            if msg := s.morshu_empty:
                await interaction.followup.send(msg)
            return

        await interaction.followup.send(file=discord.File(io.BytesIO(wav_bytes), filename="morshu.wav"))
        log(f"[MorshuCog] sent TTS file for '{text[:40]}'")

    @app_commands.command(name="morshu")
    @in_bot_channel()
    async def speak(self, interaction: discord.Interaction, text: str):
        """Join the user's voice channel and play Morshu TTS audio."""
        await interaction.response.defer()
        s = self.bot.strings
        if interaction.user.voice is None:
            if msg := s.not_in_voice.format(user=interaction.user):
                await interaction.followup.send(msg)
            return

        if msg := s.morshu_generating:
            await interaction.followup.send(msg)

        loop = asyncio.get_running_loop()
        wav_bytes = await loop.run_in_executor(None, self._generate_audio, text)

        if not wav_bytes:
            if msg := s.morshu_empty:
                await interaction.followup.send(msg)
            return

        target = interaction.user.voice.channel
        vc = interaction.guild.voice_client
        if vc is None:
            vc = await target.connect()
            if msg := s.joined_voice.format(channel=target):
                await interaction.followup.send(msg)
        elif vc.channel != target:
            await vc.move_to(target)
            if msg := s.moved_voice.format(channel=target):
                await interaction.followup.send(msg)

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
