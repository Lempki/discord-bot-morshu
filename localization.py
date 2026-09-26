"""This bot's messages and command translations, layered on top of the core ones.

The core cogs' messages live in utils/strings.py in English and Finnish.
This file adds the bot's own messages and may override any core text.
Overrides are how a bot gets its own voice.
Replies follow each user's Discord language.
LOCALE in .env picks the fallback language, and LOCALE=silent mutes public replies.

To add a language, add its Discord locale code to BOT_TEXT and COMMAND_TEXT.
Examples of codes are "de" and "sv-SE".
Any core text a language leaves out falls back to silence, and a test lists the gaps.
"""

from dataclasses import dataclass

from utils.i18n import build_locales, merge_command_text
from utils.strings import CoreStrings

__all__ = ["COMMAND_TEXT", "LOCALES", "Strings"]


@dataclass(frozen=True)
class Strings(CoreStrings):
    """The core messages plus this bot's own. Add a field here for every new message."""

    # Morshu. The placeholders of morshu_too_large are {size} and {limit} in megabytes.
    morshu_generating: str = ""
    morshu_empty: str = ""
    morshu_too_large: str = ""
    section_morshu: str = ""


# This bot's texts per language code. They override core texts that share a field name.
BOT_TEXT: dict[str, dict[str, str]] = {
    "en": {
        "morshu_generating": "Generating...",
        "morshu_empty": "Could not generate audio for that text.",
        "morshu_too_large": "The result is {size} MB, which is over this server's {limit} MB upload limit.",
        "section_morshu": "Morshu",
    },
    "fi": {
        "morshu_generating": "Luodaan...",
        "morshu_empty": "Tekstistä ei voitu luoda ääntä.",
        "morshu_too_large": "Tulos on {size} Mt, mikä ylittää tämän palvelimen {limit} Mt:n latausrajan.",
        "section_morshu": "Morshu",
    },
}

# Translations of this bot's own command descriptions, keyed by the English text.
BOT_COMMAND_TEXT: dict[str, dict[str, str]] = {
    "fi": {
        "Generate Morshu speech and send it as a file.": "Luo Morshun puhetta ja lähetä se tiedostona.",
        "The file type to create.": "Luotava tiedostotyyppi.",
        "What Morshu says, up to 500 characters.": "Mitä Morshu sanoo, enintään 500 merkkiä.",
        "WAV audio": "WAV-ääni",
        "MP4 video": "MP4-video",
        "Join your voice channel and speak as Morshu.": "Liity äänikanavallesi ja puhu Morshuna.",
    },
}

LOCALES = build_locales(Strings, BOT_TEXT)
COMMAND_TEXT = merge_command_text(BOT_COMMAND_TEXT)
