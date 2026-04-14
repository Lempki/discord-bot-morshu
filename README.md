# discord-bot-morshu

This is a Discord bot that synthesizes speech in Morshu's voice using a text-to-speech engine based on [MorshuTalk](https://github.com/n0spaces/MorshuTalk) by [n0spaces](https://github.com/n0spaces). The bot accepts arbitrary text input and generates audio by intelligently stitching phoneme segments from Morshu's original Zelda CD-i dialogue. This project is based on the [discord-bot-template](https://github.com/Lempki/discord-bot-template) repository, which provides the core architecture.

## Commands

All commands use `/` as the default prefix.

| Command | Alias | Description |
|---|---|---|
| `/tts <text>` | `/generate <text>` | Generates a WAV file from the given text and sends it as a Discord file attachment. |
| `/morshu <text>` | `/speak <text>` | Joins your current voice channel and plays the generated audio. The audio file is removed automatically after playback completes. |

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

* You must install [Git LFS](https://git-lfs.com/) because the repository uses it to manage the source audio file located in `morshutalk/`.

## Setup

You can use the included setup script to prepare the project in a single step.

On Windows, run the following command.

```
setup.bat
```

On macOS or Linux, run the following commands.

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
# Edit .env and set DISCORD_TOKEN and other values as needed
python bot.py
```

## Configuration

The base configuration variables are documented in the [discord-bot-template](https://github.com/Lempki/discord-bot-template) repository. The following variables are either specific to discord-bot-morshu or have recommended values that differ from the defaults.

| Variable | Recommended value | Description |
|---|---|---|
| `COGS_TO_LOAD` | `morshu` | This variable defines which cogs are loaded. Set it to `voice,morshu` if you also want the standalone voice channel commands. |
| `LOCALE` | `en` | This variable enables the English locale so that the bot sends status messages such as generation progress and error notifications. |

## Project structure

```
discord-bot-morshu/
├── bot.py              # Entry point.
├── config.py           # Environment variable reader. Extend this file to add new configuration keys.
├── localization.py     # Strings dataclass and locale presets. Define new languages here.
├── cogs/
│   ├── morshu.py       # Morshu TTS commands (!tts, !morshu).
│   ├── voice.py        # Voice-related commands such as join, leave, and skip.
│   └── youtube.py      # YouTube audio queue with playlist support.
├── morshutalk/         # TTS engine adapted from MorshuTalk by n0spaces.
│   ├── morshu.py       # Core phoneme matching and audio stitching logic.
│   ├── g2p.py          # Grapheme-to-phoneme conversion wrapper.
│   └── morshu.wav      # Source audio file containing Morshu's CD-i dialogue.
├── utils/
│   ├── audio.py        # Audio helpers including YouTubeDLSource and playback utilities.
│   ├── checks.py       # Custom command checks such as in_bot_channel().
│   └── logging.py      # Timestamped console logging helper.
├── assets/audio/       # Directory for audio assets. Managed via Git LFS.
├── .env.template       # Template for environment variables.
├── setup.bat           # Windows setup script.
├── setup.sh            # macOS and Linux setup script.
└── requirements.txt
```

## Credits

The TTS engine in `morshutalk/` is adapted from [MorshuTalk](https://github.com/n0spaces/MorshuTalk) by [n0spaces](https://github.com/n0spaces), released under the [MIT License](https://github.com/n0spaces/MorshuTalk/blob/main/LICENSE.txt).
