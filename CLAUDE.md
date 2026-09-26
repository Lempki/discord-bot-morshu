# discord-bot-morshu

A Discord bot that generates Morshu TTS audio and lip-synced video, with voice channel playback and file attachment delivery.
It is derived from [discord-bot-template](https://github.com/Lempki/discord-bot-template).
The shared conventions live in [discord-dev-standards](https://github.com/Lempki/discord-dev-standards), and its README is the rulebook for code, prose, and commits.

## Services

* [discord-api-morshu](https://github.com/Lempki/discord-api-morshu) generates the TTS audio and lip-synced video. This bot depends on it.
* [discord-api-media](https://github.com/Lempki/discord-api-media) can optionally handle media conversion.

## Commands

* `uv sync` installs the locked dependencies into `.venv`.
* `uv run python bot.py` starts the bot. It reads its settings from `.env`.
* `uv run pytest` runs the tests.
* `uvx pre-commit run --all-files` runs every lint and format hook.

## Layout

* `bot.py` is the entry point. It loads the cogs named in `COGS_TO_LOAD`.
* `cogs/` holds one feature group per module, including `cogs/morshu.py` for this bot's own commands.
* `utils/` holds shared helpers such as the database module and command checks.
* `localization.py` holds every user-facing message.

## Template rules

* discord-bot-template's `.template-manifest.toml` lists the core files that this bot keeps identical to it.
* Those files are changed in the template first, then carried over here with `dev-standards template-check --apply`.
* Bot-specific behavior belongs in files outside the manifest, such as `localization.py`, `compose.stack.yml`, and `cogs/morshu.py`.
* `config.py` is generic. This bot reads discord-api-morshu with `bot.config.service("morshu")`, which maps to `DISCORD_API_MORSHU_URL` and `DISCORD_API_MORSHU_SECRET`.
