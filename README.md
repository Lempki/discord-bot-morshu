# morshu

A Discord bot that synthesizes speech in Morshu's voice using a text-to-speech engine built on top of [MorshuTalk](https://github.com/n0spaces/MorshuTalk) by [n0spaces](https://github.com/n0spaces). Send any text and the bot generates audio by intelligently stitching phoneme segments from Morshu's original Zelda CD-i dialogue.

Built on [discord-bot-template](https://github.com/Lempki/discord-bot-template).

## Commands

| Command | Alias | Description |
|---|---|---|
| `!tts <text>` | `!generate <text>` | Generates a WAV file and sends it as a Discord attachment. |
| `!morshu <text>` | `!speak <text>` | Joins your voice channel and plays the generated audio. |

## Prerequisites

- Python 3.10 or newer.
- [FFmpeg](https://ffmpeg.org/) installed and available in your system PATH, or set `FFMPEG_PATH` in `.env`.

  ```
  winget install ffmpeg        # Windows
  brew install ffmpeg          # macOS
  sudo apt install ffmpeg      # Debian/Ubuntu
  ```

- [Git LFS](https://git-lfs.com/) if you plan to version control audio assets.

## Setup

Run the included setup script to prepare the project in a single step.

**Windows:**
```
setup.bat
```

**macOS / Linux:**
```
chmod +x setup.sh && ./setup.sh
```

The script creates a `.venv` virtual environment, installs all dependencies, and copies `.env.example` to `.env` on the first run. Edit `.env` and set your `DISCORD_TOKEN` before starting the bot.

If you prefer to set up manually:

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and set DISCORD_TOKEN and other values as needed
python bot.py
```

> **Note:** On the first command invocation, `g2p_en` will download NLTK data (~30 seconds). Subsequent calls are instant.

## Configuration

All configuration is read from environment variables or from a `.env` file in the project root.

| Variable | Required | Default | Description |
|---|---|---|---|
| `DISCORD_TOKEN` | Yes | — | The Discord bot token. |
| `COMMAND_PREFIX` | No | `!` | The prefix used for bot commands. |
| `FFMPEG_PATH` | No | system PATH | Absolute path to the FFmpeg binary. |
| `COGS_TO_LOAD` | No | `example` | Comma-separated list of cog modules to load. Set to `morshu` or `voice,morshu` etc. |
| `BOT_CHANNEL_ID` | No | — | Restricts command usage to a specific text channel ID. |
| `AUTO_ROLE_NAME` | No | — | Name of the role assigned when a member joins. |
| `LOCALE` | No | `silent` | Language for bot messages. Use `en` to enable responses, or `silent` to suppress them. |

## Project structure

```
morshu/
├── bot.py              # Entry point
├── config.py           # Environment variable reader
├── localization.py     # Strings dataclass and locale presets
├── cogs/
│   ├── morshu.py       # Morshu TTS commands (!tts, !morshu)
│   ├── voice.py        # Voice channel commands (join, leave, skip)
│   └── youtube.py      # YouTube audio queue with playlist support
├── morshutalk/         # TTS engine (from MorshuTalk by n0spaces)
│   ├── morshu.py       # Core phoneme matching and audio stitching
│   ├── g2p.py          # Grapheme-to-phoneme wrapper
│   └── morshu.wav      # Source audio (Morshu's CD-i dialogue)
├── utils/
│   ├── audio.py        # Audio helpers and playback utilities
│   ├── checks.py       # Custom command checks
│   └── logging.py      # Timestamped console logging helper
├── assets/audio/       # Directory for audio assets (Git LFS managed)
├── .env.example        # Template for environment variables
├── setup.bat           # Windows setup script
├── setup.sh            # macOS and Linux setup script
└── requirements.txt
```

## Credits

The TTS engine (`morshutalk/`) is based on [MorshuTalk](https://github.com/n0spaces/MorshuTalk) by [n0spaces](https://github.com/n0spaces), released under the [MIT License](https://github.com/n0spaces/MorshuTalk/blob/main/LICENSE.txt).
