import asyncio
import io
import os
import tempfile
import discord
from discord.ext import commands
from utils.checks import in_bot_channel
from utils.logging import log
from morshutalk import Morshu


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

    @commands.command(name="tts", aliases=["generate"])
    @in_bot_channel()
    async def tts(self, ctx: commands.Context, *, text: str):
        """Generate a Morshu TTS WAV and send as a file attachment."""
        s = self.bot.strings
        if msg := s.morshu_generating:
            await ctx.reply(msg)

        loop = asyncio.get_event_loop()
        wav_bytes = await loop.run_in_executor(None, self._generate_audio, text)

        if not wav_bytes:
            if msg := s.morshu_empty:
                await ctx.reply(msg)
            return

        await ctx.reply(file=discord.File(io.BytesIO(wav_bytes), filename="morshu.wav"))
        log(f"[MorshuCog] sent TTS file for '{text[:40]}'")

    @commands.command(name="morshu", aliases=["speak"])
    @in_bot_channel()
    async def speak(self, ctx: commands.Context, *, text: str):
        """Join the user's voice channel and play Morshu TTS audio."""
        s = self.bot.strings
        if ctx.author.voice is None:
            if msg := s.not_in_voice.format(user=ctx.author):
                await ctx.reply(msg)
            return

        if msg := s.morshu_generating:
            await ctx.reply(msg)

        loop = asyncio.get_event_loop()
        wav_bytes = await loop.run_in_executor(None, self._generate_audio, text)

        if not wav_bytes:
            if msg := s.morshu_empty:
                await ctx.reply(msg)
            return

        target = ctx.author.voice.channel
        vc = ctx.voice_client
        if vc is None:
            vc = await target.connect()
            if msg := s.joined_voice.format(channel=target):
                await ctx.reply(msg)
        elif vc.channel != target:
            await vc.move_to(target)
            if msg := s.moved_voice.format(channel=target):
                await ctx.reply(msg)

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

    async def cog_command_error(self, ctx: commands.Context, error: Exception):
        if isinstance(error, commands.CheckFailure):
            return
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply(f"Missing required argument: `{error.param.name}`")
        else:
            raise error

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"[{self.__class__.__name__}] loaded.")


async def setup(bot: commands.Bot):
    await bot.add_cog(MorshuCog(bot))
