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
* `utils/strings.py` holds the core cogs' messages in every language, and `localization.py` adds this bot's own.

## Template rules

* discord-bot-template's `.template-manifest.toml` lists the core files that this bot keeps identical to it.
* Those files are changed in the template first, then carried over here with `dev-standards template-check --apply`.
* Bot-specific behavior belongs in files outside the manifest, such as `localization.py`, `compose.stack.yml`, and `cogs/morshu.py`.
* `config.py` is generic. This bot reads discord-api-morshu with `bot.config.service("morshu")`, which maps to `DISCORD_API_MORSHU_URL` and `DISCORD_API_MORSHU_SECRET`.

## Messages and languages

* Never hard-code user-facing text in a cog. Add a field to `Strings` in `localization.py`, give it text in every language, and send it with `respond()`.
* Pick the language with `self.bot.strings_for(interaction)`. Pass `private=True` for ephemeral admin and moderator replies, which stay on even when `LOCALE=silent`.
* A command that defers must end with a reply or with `finish(interaction)`, so it never keeps showing "is thinking...".
* A reply sent without `respond()`, such as a file follow-up, must be followed by `mark_replied(interaction)`.
* A command's docstring is its Discord description. Keep it under 100 characters, describe every option, and add the Finnish translation of each text to `BOT_COMMAND_TEXT`.
* Voice goes through `self.bot.voice_presence`, which joins, plays, and leaves idle or empty channels. `cogs/morshu.py` plays generated audio with `bytes_source()`.
* `uv run pytest` fails when a language misses a message or a command translation.
