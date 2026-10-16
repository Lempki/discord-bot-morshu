"""This bot's messages and command translations, layered on top of the core ones.

The core cogs' messages live in utils/strings.py in English and Finnish.
This file adds the bot's own messages and may override any core text.
Overrides are how a bot gets its own voice.
Replies follow each user's Discord language.
LOCALE in .env picks the fallback language, and LOCALE=silent mutes public replies.

To add a language, add its Discord locale code to BOT_TEXT and BOT_COMMAND_TEXT.
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
    morshu_send_failed: str = ""
    section_morshu: str = ""
    guide_morshu: str = ""


# This bot's texts per language code. They override core texts that share a field name.
BOT_TEXT: dict[str, dict[str, str]] = {
    "en": {
        "morshu_generating": "Generating...",
        "morshu_empty": "Could not generate speech for that text.",
        "morshu_too_large": "The result is {size} MB, which is over this server's {limit} MB upload limit.",
        "morshu_send_failed": "The file did not reach Discord. Try again.",
        "section_morshu": "Morshu",
        "status_idle": "Lamp oil, rope, bombs? /help",
        "mention_reply": "You want it? It's yours, my friend. The guide opens only for you.",
        "help_intro": "Morshu speaks any text in his own voice, in your voice channel or as a file. Each part below explains one of his features.",
        "guide_morshu": "`/morshu` speaks your text in your voice channel, and `/generate` sends it as a WAV file or a lip-synced MP4 video. A text holds up to 500 characters, and it shows in the chat, so everyone sees what Morshu said. Morshu keeps none of your texts: [privacy policy](https://github.com/Lempki/discord-bot-morshu/blob/main/PRIVACY.md) and [terms](https://github.com/Lempki/discord-bot-morshu/blob/main/TERMS.md).",
    },
    "fi": {
        "morshu_generating": "Luodaan...",
        "morshu_empty": "Tekstistä ei voitu luoda puhetta.",
        "morshu_too_large": "Tulos on {size} Mt, mikä ylittää tämän palvelimen {limit} Mt:n latausrajan.",
        "morshu_send_failed": "Tiedosto ei päässyt Discordiin. Yritä uudelleen.",
        "section_morshu": "Morshu",
        "status_idle": "Lamppuöljyä, köyttä, pommeja? /help",
        "mention_reply": "Haluatko sen? Se on sinun, ystäväni. Ohje aukeaa vain sinulle.",
        "help_intro": "Morshu puhuu minkä tahansa tekstin omalla äänellään, äänikanavallasi tai tiedostona. Jokainen alla oleva osa kertoo yhdestä hänen ominaisuudestaan.",
        "guide_morshu": "`/morshu` puhuu tekstisi äänikanavallasi, ja `/generate` lähettää sen WAV-tiedostona tai huulisynkronoituna MP4-videona. Tekstiin mahtuu 500 merkkiä, ja se näkyy keskustelussa, joten kaikki näkevät, mitä Morshu sanoi. Morshu ei säilytä tekstejäsi: [tietosuojaseloste](https://github.com/Lempki/discord-bot-morshu/blob/main/PRIVACY.md) ja [käyttöehdot](https://github.com/Lempki/discord-bot-morshu/blob/main/TERMS.md).",
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
