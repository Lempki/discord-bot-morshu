# discord-bot-morshu

This is a Discord bot that generates speech in Morshu's voice by calling the [discord-api-morshu](https://github.com/Lempki/discord-api-morshu) API. This project is based on the [discord-bot-template](https://github.com/Lempki/discord-bot-template) repository, which provides the core architecture.

## Commands

| Command | Description |
|---|---|
| `/generate <format> <text>` | Generates audio or video from the given text and sends it as a file attachment. `format` choices are `WAV audio` and `MP4 video`. |
| `/morshu <text>` | Joins your current voice channel and plays the generated audio. The audio file is removed automatically after playback completes. |
| `/help` | Displays all loaded commands grouped by cog in an ephemeral embed. |

## Prerequisites

* You must have Python 3.12 installed on your system.
* You must install [uv](https://docs.astral.sh/uv/). On Windows, run `winget install --id astral-sh.uv`. On macOS or Linux, follow the uv installation guide.
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

The script runs `uv sync`, which creates the `.venv` virtual environment if needed and installs the locked dependencies. It copies `.env.template` to `.env` on the first run. You must edit `.env` and set your `DISCORD_TOKEN` before starting the bot.

If you prefer to perform the setup manually, follow these steps:

```bash
git clone https://github.com/Lempki/discord-bot-morshu.git
cd discord-bot-morshu
uv sync
cp .env.template .env
# Edit .env and set DISCORD_TOKEN and other values as needed.
uv run python bot.py
```

### Development

Run the tests with `uv run pytest`.
Run every lint and format check with `uvx pre-commit run --all-files`, or install the hooks once with `uvx pre-commit install` so they run on each commit.
The coding, prose, and commit conventions are documented in [discord-dev-standards](https://github.com/Lempki/discord-dev-standards).

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
| `COGS_TO_LOAD` | `help,morshu` | Cogs to load at startup. Use `help,voice,morshu` to add voice channel commands, or `help,voice,media,morshu,admin,moderation` for the full feature set. |
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
│   ├── media.py        # Audio queue with YouTube and Spotify support.
│   ├── admin.py        # /admin command group for per-guild configuration.
│   ├── moderation.py   # /warn, /warnings, /clearwarning, /clearwarnings, /kick, /ban.
│   └── template.py     # Reference cog inherited from discord-bot-template. Not loaded by default.
├── utils/
│   ├── audio.py        # MediaAPIClient, URL helpers, and local file playback utility.
│   ├── checks.py       # Custom command checks such as in_bot_channel().
│   ├── database.py     # aiosqlite singleton, per-guild settings and warnings CRUD.
│   └── logging.py      # Timestamped console logging helper.
├── assets/
│   ├── audio/          # .ogg, .mp3, .wav — Git LFS
│   ├── images/         # .png, .jpg, .gif, .webp — Git LFS
│   └── videos/         # .mp4, .mov, .webm — Git LFS
├── tests/              # Pytest suite. Runs in CI on every push.
├── .env.template       # Template for environment variables.
├── pyproject.toml      # Project metadata and dependencies.
├── uv.lock             # Locked dependency versions.
├── ruff.toml           # Lint and format settings on top of the shared baseline.
├── setup.bat           # Windows setup script.
├── setup.sh            # macOS and Linux setup script.
├── Dockerfile
├── docker-compose.yml
└── .dockerignore
```

## Staying in sync with the template

This repository does not maintain a git link to discord-bot-template.
Instead, discord-bot-template's `.template-manifest.toml` lists the core files that this bot keeps identical to it.
With both repositories cloned side by side, run this from this bot's directory to see which core files have drifted:

```bash
uvx --from git+https://github.com/Lempki/discord-dev-standards@v0.1.1 dev-standards template-check --template ../discord-bot-template --diff
```

Add `--apply` to copy the template's version over every drifted file, then review the result with `git diff` before committing.
Keep bot-specific changes in files outside the manifest, such as `config.py`, `localization.py`, and `cogs/morshu.py`.

## Related services

The following services work alongside this bot and handle functionality that is managed centrally rather than bundled in each bot repository.

| Service | Description |
|---|---|
| [discord-api-morshu](https://github.com/Lempki/discord-api-morshu) | Hosts the Morshu TTS engine. Accepts text and returns a synthesised WAV or video file. The source audio and sprite assets live here. |
| [discord-api-media](https://github.com/Lempki/discord-api-media) | Resolves YouTube, SoundCloud, and Spotify track metadata and stream URLs. Bots call this instead of bundling yt-dlp directly. |
