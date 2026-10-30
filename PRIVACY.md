# Privacy policy

This policy explains what the Discord bot Morshu does with information about you.
It applies to the public Morshu that Axel Lindberg runs, which you can add to a Discord server.
Someone who runs their own copy of this source code is responsible for their own copy.

Effective date: 30 October 2026.

## Who is responsible

Axel Lindberg runs Morshu as a personal hobby project and is the controller of the information below under the EU General Data Protection Regulation (GDPR).
You can reach Axel Lindberg at [esa.kempli@gmail.com](mailto:esa.kempli@gmail.com).

## What Morshu does with the text you give it

* `/generate` and `/morshu` take a text of up to 500 characters and turn it into speech in Morshu's voice.
* The text goes to api-morshu, the speech service that runs on the same computer as the bot. It is not sent to any other service.
* Neither the bot nor api-morshu saves the text, and neither writes it to a log.
* The audio and the video exist only in memory, until Discord has received the file from `/generate`, or until `/morshu` has finished playing in your voice channel. While api-morshu makes a video, the audio passes through a temporary file that is also kept in memory, never reaches the disk, and is deleted as soon as the video is made.
* Morshu posts the text in the channel, so that moderators can see what was generated: together with the file for `/generate`, and as its own message for `/morshu`. Discord stores that message like any other message in the channel, and the server's moderators can delete it.

## What Morshu receives from Discord

To work, Morshu receives what Discord gives every bot in a server, such as the server's channels and roles, member names and IDs, and who is in which voice channel.
Morshu uses this only to answer commands, for example to join the voice channel you are in.
It does not save any of it.

Discord also gives Morshu the text of a message that mentions Morshu.
Morshu only checks whether the message is nothing but the mention, and then answers with a button that opens its guide.
It does not save the text, does not write it to a log, and reads no other messages.
Morshu does not ask Discord for direct messages, so the text of a direct message never reaches it.

## What Morshu stores

* **A database.** The public Morshu stores no information about members. The database exists for optional moderation features, such as warnings, which the public Morshu does not offer.
* **Technical logs.** The computer that runs Morshu keeps logs of what the bot does, such as which server a command came from, which command ran, and any errors. The logs contain server names and IDs, and the ID that Discord gives each command, which ties the bot's and api-morshu's lines about that command together. They contain no message texts, no member names, and no channel names. Each part of the bot keeps at most two log files of 5 MB, and the oldest lines are overwritten as new ones come in. A part's logs are also deleted when an update replaces that part.

## Why this is allowed

Morshu handles the information above because you ask it to, by running its commands or by adding it to your server.
Under the GDPR, this rests on the legitimate interest in providing the feature you asked for, under Article 6(1)(f).

## Who else sees it

Nobody else receives information from Morshu.
Discord itself processes everything you do on Discord, including your commands to Morshu, under [Discord's privacy policy](https://discord.com/privacy).

## Your rights

You may ask what information about you Morshu holds, and ask for it to be corrected or deleted.
Since Morshu stores no information about members, the answer will usually be that there is none.
Send requests to [esa.kempli@gmail.com](mailto:esa.kempli@gmail.com).
You may also complain to the Finnish data protection authority, the [Data Protection Ombudsman](https://tietosuoja.fi/en), or to the authority of the EU country you live in.

## Children

Morshu is meant for people who meet Discord's minimum age in their country.

## Changes

A changed policy is published in this file, with a new effective date.
The history of every change is visible in the [repository](https://github.com/Lempki/discord-bot-morshu/commits/main/PRIVACY.md).
