# discord-bot-morshu

This is a Discord bot that generates speech in Morshu's voice by calling the [discord-api-morshu](https://github.com/Lempki/discord-api-morshu) API. This project is based on the [discord-bot-template](https://github.com/Lempki/discord-bot-template) repository, which provides the core architecture.

## Commands

| Command | Description |
|---|---|
| `/generate <format> <text>` | Generates audio or video from the given text and sends it as a file attachment. `format` choices are `WAV audio` and `MP4 video`. |
| `/morshu <text>` | Joins your current voice channel and plays the generated audio. The audio file is removed automatically after playback completes. |
| `/help` | Displays all loaded commands grouped by cog in an ephemeral embed. |

## Prerequisites

* You must have Python version 3.10 or newer installed on your system.
* You must install [FFmpeg](https://ffmpeg.org/) and ensure that it is available in your system PATH. You may alternatively define a custom path using the `FFMPEG_PATH` environment variable.

  * On Windows, install FFmpeg with the following command:

    ```
    winget install ffmpeg
    ```

  * On macOS, install FFmpeg with the following command:

    ```
    brew install ffmpeg
    ```

  * On Debian or Ubuntu, install FFmpeg with the following command:
  
    ```
    sudo apt install ffmpeg
    ```


## Privileged intents

The same privileged intents as the base template are required. See the [discord-bot-template](https://github.com/Lempki/discord-bot-template) repository for details.

## Bot permissions

All base permissions from the [discord-bot-template](https://github.com/Lempki/discord-bot-template) are required, plus the following addition:

| Permission | Required for |
|---|---|
| Attach Files | Sending generated WAV files as Discord file attachments. |

## Setup

You can use the included setup script to prepare the project in a single step.

On Windows, run the following command:

```
setup.bat
```

On macOS or Linux, run the following commands:

```
chmod +x setup.sh
./setup.sh
```

The script creates a `.venv` virtual environment if one does not already exist. It installs all required dependencies and copies `.env.template` to `.env` on the first run. You must edit `.env` and set your `DISCORD_TOKEN` before starting the bot.

If you prefer to perform the setup manually, follow these steps:

```bash
git clone https://github.com/Lempki/discord-bot-morshu.git
cd discord-bot-morshu
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.template .env
# Edit .env and set DISCORD_TOKEN and other values as needed.
python bot.py
```

### Docker

Alternatively, you can run the bot as a Docker container.

1. Copy `.env.template` to `.env` and set `DISCORD_TOKEN`.
2. Build and start the container:

   ```
   docker-compose up -d
   ```

The container automatically restarts unless explicitly stopped.

## Configuration

The base configuration variables are documented in the [discord-bot-template](https://github.com/Lempki/discord-bot-template) repository. The following variables are either specific to discord-bot-morshu or behave differently from the template defaults.

| Variable | Default | Description |
|---|---|---|
| `COGS_TO_LOAD` | `template` | Cogs to load at startup. Set to `help,morshu` for TTS-only, `help,voice,morshu` to add voice channel commands, or `help,voice,media,morshu` for the full feature set. |
| `LOCALE` | `silent` | Bot message language. Set to `en` to enable status messages such as generation progress and error notifications. |
| `DISCORD_API_TTS_URL` | — | Base URL of the [discord-api-morshu](https://github.com/Lempki/discord-api-morshu) service. Required when the `morshu` cog is loaded. |
| `DISCORD_API_TTS_SECRET` | — | Bearer token for the discord-api-morshu service. Must match `DISCORD_API_SECRET` in the service configuration. |

## Project structure

```
discord-bot-morshu/
├── bot.py              # Entry point.
├── config.py           # Environment variable reader. Extend this file to add new configuration keys.
├── localization.py     # Strings dataclass and locale presets. Define new languages here.
├── cogs/
│   ├── help.py         # /help command. Lists all loaded commands grouped by cog.
│   ├── morshu.py       # Morshu TTS commands (/generate, /morshu).
│   ├── voice.py        # Voice-related commands such as join, leave, and skip.
│   └── media.py        # Audio queue with YouTube and Spotify support.
├── utils/
│   ├── audio.py        # MediaAPIClient, URL helpers, and local file playback utility.
│   ├── checks.py       # Custom command checks such as in_bot_channel().
│   └── logging.py      # Timestamped console logging helper.
├── assets/
│   ├── audio/          # .ogg, .mp3, .wav — Git LFS
│   ├── images/         # .png, .jpg, .gif, .webp — Git LFS
│   └── videos/         # .mp4, .mov, .webm — Git LFS
├── .env.template       # Template for environment variables.
├── setup.bat           # Windows setup script.
├── setup.sh            # macOS and Linux setup script.
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
└── requirements.txt
```

## Related services

The following services work alongside this bot and handle functionality that is managed centrally rather than bundled in each bot repository.

| Service | Description |
|---|---|
| [discord-api-morshu](https://github.com/Lempki/discord-api-morshu) | Hosts the Morshu TTS engine. Accepts text and returns a synthesised WAV or video file. The source audio and sprite assets live here. |
| [discord-api-media](https://github.com/Lempki/discord-api-media) | Resolves YouTube, SoundCloud, and Spotify track metadata and stream URLs. Bots call this instead of bundling yt-dlp directly. |

