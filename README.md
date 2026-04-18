# discord-bot-morshu

This is a Discord bot that synthesizes speech in Morshu's voice using a text-to-speech engine based on [MorshuTalk](https://github.com/n0spaces/MorshuTalk) by [n0spaces](https://github.com/n0spaces). The bot accepts arbitrary text input and generates audio by intelligently stitching phoneme segments from Morshu's original Zelda CD-i dialogue. This project is based on the [discord-bot-template](https://github.com/Lempki/discord-bot-template) repository, which provides the core architecture. The TTS engine and its source assets are hosted as a standalone service in [discord-api-tts](https://github.com/Lempki/discord-api-tts).

## Commands

| Command | Description |
|---|---|
| `/generate <text>` | Generates a WAV file from the given text and sends it as a Discord file attachment. |
| `/morshu <text>` | Joins your current voice channel and plays the generated audio. The audio file is removed automatically after playback completes. |

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
source .venv/bin/activate
# On Windows use: .venv\Scripts\activate
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
| `COGS_TO_LOAD` | `template` | Cogs to load at startup. Set to `morshu` for TTS-only mode, or `voice,morshu` to also include standalone voice channel commands. |
| `LOCALE` | `silent` | Bot message language. Set to `en` to enable status messages such as generation progress and error notifications. |

## Project structure

```
discord-bot-morshu/
├── bot.py              # Entry point.
├── config.py           # Environment variable reader. Extend this file to add new configuration keys.
├── localization.py     # Strings dataclass and locale presets. Define new languages here.
├── cogs/
│   ├── morshu.py       # Morshu TTS commands (/generate, /morshu).
│   ├── voice.py        # Voice-related commands such as join, leave, and skip.
│   └── youtube.py      # YouTube audio queue with playlist support.
├── morshutalk/         # TTS engine adapted from MorshuTalk by n0spaces.
│   ├── morshu.py       # Core phoneme matching and audio stitching logic.
│   └── g2p.py          # Grapheme-to-phoneme conversion wrapper.
├── utils/
│   ├── audio.py        # Audio helpers including YouTubeDLSource and playback utilities.
│   ├── checks.py       # Custom command checks such as in_bot_channel().
│   └── logging.py      # Timestamped console logging helper.
├── assets/audio/       # Directory for audio assets. Managed via Git LFS.
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
| [discord-api-tts](https://github.com/Lempki/discord-api-tts) | Hosts the Morshu TTS engine. Accepts text and returns a synthesised WAV or video file. The source audio and video assets live here. |
| [discord-api-media](https://github.com/Lempki/discord-api-media) | Resolves YouTube and SoundCloud track metadata and stream URLs. Bots call this instead of bundling yt-dlp directly. |

## Credits

The TTS engine in `morshutalk/` is adapted from [MorshuTalk](https://github.com/n0spaces/MorshuTalk) by [n0spaces](https://github.com/n0spaces), released under the [MIT License](https://github.com/n0spaces/MorshuTalk/blob/main/LICENSE.txt).
