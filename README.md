# discord-bot-morshu

This is a Discord bot that generates speech in Morshu's voice by calling the [discord-api-morshu](https://github.com/Lempki/discord-api-morshu) API. This project is based on the [discord-bot-template](https://github.com/Lempki/discord-bot-template) repository, which provides the core architecture.

## Commands

| Command | Description |
|---|---|
| `/generate <format> <text>` | Generates audio or video from the given text and sends it as a file attachment. `format` choices are `WAV audio` and `MP4 video`. A result over the server's upload limit is not sent. |
| `/morshu <text>` | Joins your current voice channel and plays the generated audio. The bot leaves on its own when it is alone or after 10 minutes of silence. |
| `/help` | Displays all loaded commands grouped by cog in an ephemeral embed. |

Adding `admin` and `moderation` to `COGS_TO_LOAD` enables the template's moderation commands, including AutoMod management under `/admin automod`.
See the [template README](https://github.com/Lempki/discord-bot-template#moderation-and-automod).

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

All base permissions from the [discord-bot-template](https://github.com/Lempki/discord-bot-template) are required.
Attach Files, which `/generate` uses, is one of them.
Manage Server and Moderate Members are needed only when the `admin` and `moderation` cogs are loaded.

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

1. Copy `.env.template` to `.env` and set `DISCORD_TOKEN`, `DISCORD_API_MORSHU_URL`, and `DISCORD_API_MORSHU_SECRET`.
2. Build and start the container:

   ```
   docker compose up -d --build
   ```

The container restarts automatically unless you stop it.
The database lives on the `bot-data` volume, so settings and warnings survive rebuilds and `docker compose down`.
Only `docker compose down -v` deletes it.

To also run discord-api-morshu, clone it next to this repository and use the stack file instead:

```
docker compose -f compose.stack.yml up -d --build
```

Add `--profile media` to also run discord-api-media, cloned next to this repository the same way.
The stack builds each service from its sibling folder and connects them on a private network.
It passes `DISCORD_API_MORSHU_SECRET`, and `DISCORD_API_MEDIA_SECRET` when the media profile is used, from this repository's `.env` to the matching service, so the bot and each service always agree.

## Configuration

The base configuration variables are documented in the [discord-bot-template](https://github.com/Lempki/discord-bot-template) repository. The following variables are either specific to discord-bot-morshu or behave differently from the template defaults.

| Variable | Default | Description |
|---|---|---|
| `COGS_TO_LOAD` | `help,morshu` | Cogs to load at startup. Use `help,voice,morshu` to add voice channel commands, or `help,voice,media,morshu,admin,moderation` for the full feature set. |
| `LOCALE` | `silent` | The fallback language for users whose Discord language the bot does not speak. Built-in values are `en` and `fi`. `silent` mutes public replies, such as generation progress and error notifications, while admin and moderator replies are still sent because only the person who ran the command sees them. |
| `DISCORD_API_MORSHU_URL` | — | Base URL of the [discord-api-morshu](https://github.com/Lempki/discord-api-morshu) service. Required when the `morshu` cog is loaded. `compose.stack.yml` overrides this inside the stack. |
| `DISCORD_API_MORSHU_SECRET` | — | Bearer token for the discord-api-morshu service. Must match `DISCORD_API_SECRET` in the service configuration. |

## Project structure

```
discord-bot-morshu/
├── bot.py              # Entry point.
├── config.py           # Reads settings and discord-api-* service URLs from the environment.
├── localization.py     # This bot's own messages and translations, layered on the core ones.
├── cogs/
│   ├── help.py         # /help command. Lists all loaded commands grouped by cog.
│   ├── morshu.py       # Morshu TTS commands (/generate, /morshu).
│   ├── voice.py        # /join, /leave, and /skip. The bot leaves on its own when alone or idle.
│   ├── media.py        # Per-server audio queue with YouTube, SoundCloud, and Spotify support.
│   ├── admin.py        # /admin command group, including /admin automod.
│   ├── moderation.py   # /warn, /warnings, /clearwarning, /clearwarnings, /kick, /ban, and AutoMod escalation.
│   └── template.py     # Reference cog inherited from discord-bot-template. Not loaded by default.
├── utils/
│   ├── audio.py        # MediaAPIClient, URL helpers, and audio sources for files, bytes, and streams.
│   ├── automod.py      # Creates and edits the AutoMod rules that the bot owns.
│   ├── checks.py       # Command checks such as in_bot_channel(), and guild_of().
│   ├── database.py     # Versioned SQLite schema, per-guild settings, and warnings.
│   ├── i18n.py         # Picks each user's language and translates command descriptions.
│   ├── moderation.py   # issue_warning(), shared by /warn and AutoMod escalation.
│   ├── replies.py      # respond() and finish(), which never leave a command "thinking".
│   ├── strings.py      # Every core message and command translation, in English and Finnish.
│   └── voice.py        # Joins, plays in, and leaves voice channels for every cog.
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
├── docker-compose.yml  # Runs the bot alone, with its database on a volume.
├── compose.stack.yml   # Runs the bot together with the discord-api-* services it uses.
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
Keep bot-specific changes in files outside the manifest, such as `localization.py`, `compose.stack.yml`, and `cogs/morshu.py`.

## Localization

Replies follow the Discord language of the user who ran the command.
A user whose language the bot does not speak gets the `LOCALE` language, and English after that.
Messages without an interaction, such as the join welcome, use the server's preferred language.

Command descriptions, option descriptions, and choice names are localized natively, so each user's Discord client shows them in their own language.
Command and option names always stay English, so everyone types the same commands.

The core cogs' messages and command translations live in `utils/strings.py`, in English and Finnish.
This bot's own messages and the translations of `/generate` and `/morshu` live in `localization.py`, also in English and Finnish.
To add a language, add its Discord locale code, such as `de` or `sv-SE`, to `BOT_TEXT` and `BOT_COMMAND_TEXT` in `localization.py`.

The tests list every message or command text a language is missing, and they fail on command texts longer than Discord's 100-character limit.

## Related services

The following services work alongside this bot and handle functionality that is managed centrally rather than bundled in each bot repository.

| Service | Description |
|---|---|
| [discord-api-morshu](https://github.com/Lempki/discord-api-morshu) | Hosts the Morshu TTS engine. Accepts text and returns a synthesised WAV or video file. The source audio and sprite assets live here. |
| [discord-api-media](https://github.com/Lempki/discord-api-media) | Resolves YouTube, SoundCloud, and Spotify track metadata and stream URLs. Bots call this instead of bundling yt-dlp directly. |
