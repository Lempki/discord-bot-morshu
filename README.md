# discord-bot-morshu

This is a Discord bot that generates speech in Morshu's voice by calling the api-morshu API, a private speech service. This project is based on the [discord-bot-template](https://github.com/Lempki/discord-bot-template) repository, which provides the core architecture.

## Commands

| Command | Description |
|---|---|
| `/generate <format> <text>` | Generates audio or video from the given text and sends it as a file attachment. `format` choices are `WAV audio` and `MP4 video`. `text` holds up to 500 characters. The text shows above the file exactly as typed, so moderators and moderation bots can see what was generated. It never pings anyone. A result over the server's upload limit is not sent. |
| `/morshu <text>` | Joins your current voice channel and plays the generated audio. `text` holds up to 500 characters. The text also shows in the chat exactly as typed, without pinging anyone, so moderators can see what was spoken. The bot leaves on its own when it is alone or after 10 minutes of silence. While it plays in another voice channel, it answers that it is busy instead of moving. |
| `/help` | Shows a short guide to Morshu and the commands you can use, with links to the privacy policy and terms, in an embed that only you see. A message that only mentions Morshu gets a short reply with a button that opens the same guide, and the reply deletes itself after a minute. |
| `/about` | Shows the bot's version, how long it has been online, its response time, and a link to its source code, in a reply that only you see. |

These are the commands of the default cogs, `help` and `morshu`.
`/generate` and `/morshu` work only in servers.
Each member can run each of them twice within 20 seconds, because speech takes the most CPU of anything the bot does.

Adding `voice` to `COGS_TO_LOAD` adds `/voice join`, `/voice leave`, and `/voice stop`, which stops a speech that plays.
Adding `admin` and `moderation` enables the template's moderation commands, including AutoMod management under `/admin automod`.
With `admin` loaded, `/admin channel` can restrict `/generate`, `/morshu`, and the voice and media commands to one bot channel.
Adding `events` gives new members the role set with `/admin autorole` and posts a welcome message in the bot channel, and with `/admin goodbye` a goodbye when a member leaves, so load it together with `admin`.
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

With its default cogs, `help` and `morshu`, the bot needs no privileged intent, so leave all of them disabled.
Adding `events` to `COGS_TO_LOAD` makes the bot ask for Server Members, for the auto-role and the welcome message on member join, and the goodbye when a member leaves.
Then enable **Server Members Intent** under **Privileged Gateway Intents** on your application's **Bot** page in the [Discord Developer Portal](https://discord.com/developers/applications) before starting the bot, or Discord refuses the connection.
A verified bot needs Discord's approval for every privileged intent it asks for.

The **Presence Intent** and the **Message Content Intent** are not needed and should stay disabled.
Discord gives a bot the text of a message that mentions it without the Message Content Intent, which is all that the reply to a mention needs.
The bot turns off the direct messages intent, so Discord never sends it the text of a direct message. Slash commands and buttons still work in direct messages, because they are interactions.
The bot also requests the Auto Moderation Execution intent, which is not privileged and needs no portal setting.

## Bot permissions

Use the **OAuth2 > URL Generator** in the Developer Portal to build the invite URL.
Select the `bot` and `applications.commands` scopes, then select the permissions below.

The default cogs, `help` and `morshu`, need these permissions.

| Permission | Required for |
|---|---|
| View Channels | Reading channel state. |
| Send Messages | Answering a message that only mentions Morshu. Command replies need no permission. |
| Attach Files | Sending the files that `/generate` creates. |
| Connect | Joining a voice channel for `/morshu`. |
| Speak | Playing the generated audio for `/morshu`. |
| Read Message History | Optional. Replying to a message that only mentions Morshu. Without it, Morshu answers in the channel instead. |

The `voice` cog needs no further permissions.
The other optional cogs add these permissions.

| Cog | Additional permissions |
|---|---|
| `media` | Embed Links, for the now-playing panel. Set Voice Channel Status is optional, for showing the playing song under the voice channel's name. |
| `admin` | Manage Server, for managing the bot's AutoMod rules with `/admin automod`. |
| `moderation` | Kick Members for `/kick`, Ban Members for `/ban`, Moderate Members for `/timeout`, `/untimeout`, and the `timeout` warning action, and Manage Messages with Read Message History for `/purge`. Embed Links lets the right-click Report to moderators post its embed. The `kick` and `ban` warning actions use the first two. AutoMod escalation also needs Manage Server, because Discord only delivers AutoMod executions to bots that have it. |
| `events` | Manage Roles, for giving new members the auto-role. Ban Members is optional, and tells a ban from a leave, so a banned member gets no goodbye. |

Discord's role settings call Moderate Members **Timeout Members**.

## Setup

The setup script prepares the project in a single run, and it is safe to run again at any time.

On Windows, double-click `setup.bat` or run it from a terminal:

```
setup.bat
```

On macOS or Linux, run the following commands:

```
chmod +x setup.sh
./setup.sh
```

The script asks before it installs or starts anything, and it does the following:

1. It installs [uv](https://docs.astral.sh/uv/) when uv is missing. uv also provides Python 3.12 when the machine lacks it.
2. It offers to install Docker, and in a Git clone also the tools that the Docker image includes for running outside Docker, such as FFmpeg. It uses winget on Windows, Homebrew on macOS, and the system package manager on Linux. On Windows it also turns on WSL, which Docker Desktop needs, and says when Windows needs a restart or virtualization is turned off in the firmware. It shows the computer's RAM and offers to cap the memory of Docker Desktop's virtual machine, at a suggested or your own size.
3. In a Git clone, it runs `uv sync`, which installs the locked dependencies into `.venv`.
4. It copies `.env.template` to `.env` on the first run and asks for the bot token, which it reads without showing it. When `LOCALE` is not set, it explains that the default mutes public replies and asks for the bot's language.
5. It prepares `compose.stack.yml`. It fills each API secret that the stack needs and reuses the service's own `API_SECRET` when that service is already set up. A downloaded release runs the images that GitHub publishes, so it needs no other repository. In a Git clone, when an api-* repository that the stack builds is missing, it looks for a downloaded release of it, also inside the extra folder that Windows' Extract All creates, and moves it into place. Otherwise it clones the repository. It then starts Docker Desktop when it is not running, and offers to start the bot and its services in Docker.
6. In a downloaded release, it offers to install new releases automatically every night.

A step that fails says what went wrong, why it matters, and what to do next, and the summary at the end lists it again.
The steps live in `scripts/bootstrap.py`, which needs only the Python standard library.

If you prefer to perform the setup manually, follow these steps:

```bash
git clone https://github.com/Lempki/discord-bot-morshu.git
cd discord-bot-morshu
uv sync
cp .env.template .env
# Edit .env and set DISCORD_TOKEN and other values as needed.
uv run python bot.py
```

### Running

After setup has run once, the run script starts the bot.
Double-click `run.bat` on Windows, or run `./run.sh` on macOS and Linux.
It starts the bot and the api-* services in `compose.stack.yml` in Docker in the background.
It then waits until every service is ready and shows their status.
The containers then start again whenever Docker starts.

The script also takes an action, such as `run.bat stop` on Windows or `./run.sh stop` elsewhere:

| Action | What it does |
|---|---|
| `start` | Starts everything in Docker and waits until it is ready. It is the default. |
| `stop` | Stops the containers. They stay stopped until the next start. |
| `status` | Shows whether each container runs and is healthy, its version, and whether updates are automatic. |
| `logs` | Follows the logs. Press Ctrl+C to stop following. |
| `update` | Installs the newest release. In a Git clone, it pulls the latest code, rebuilds on fresh base images, and restarts, then deletes the build cache that no build used for a week. |
| `schedule` | Installs new releases automatically every night at 04:00. |
| `unschedule` | Stops installing new releases automatically. |
| `backup` | Copies the bot's database into the `backups` folder. Every update does it too. |
| `restore` | Puts a backup of the bot's database back. It asks which one and backs up the current database first. |
| `local` | Runs the project in the terminal without Docker. Press Ctrl+C to stop it. |

When a service crashes right after it starts, the script shows the end of its log and stops it, so it does not restart over and over.
In a Git clone, the `update` action also pulls the api-* repositories that the stack builds.
The `local` action runs only the bot, which reaches its services at the URLs in `.env`.

### Updates

A downloaded release runs the Docker images that GitHub publishes for every release, such as `ghcr.io/lempki/api-media`.
A Git clone builds the images from its own files instead.

In a downloaded release, the `update` action takes these steps:

1. It backs up the bot's database, as the `backup` action does.
2. It downloads the newest image of the bot and of each service in `compose.stack.yml`.
3. When the bot's image is new, it replaces the run, setup, and compose files with the ones from the new release. `.env` and the other settings stay as they are.
4. It restarts everything and waits until every service is ready.
5. When the new release fails to start, it puts the previous images and files back and starts them again. Later updates skip that release until a newer one appears.
6. It deletes the images that nothing uses anymore, such as the versions that the new release replaced.

The `schedule` action runs this update every night at 04:00.
On Windows it adds a task to the Task Scheduler, which runs as soon as the computer is on again when it was off or asleep at that time.
On macOS and Linux it adds a line to your crontab.
Each scheduled update writes what it did into `update.log` in the project folder. With `UPDATE_WEBHOOK_URL` in `.env` set to a Discord webhook, an update that installs a new release or fails also posts a short message to that webhook's channel, naming the new versions or the problem. A night without a new release posts nothing. To get a webhook, open a channel's settings in Discord, choose Integrations, then Webhooks, then New Webhook, and copy its URL.

A private image needs a GitHub sign-in.
The first download asks for a [token with the `read:packages` scope](https://github.com/settings/tokens/new?scopes=read:packages&description=Docker+updates), which Docker then remembers.

### Backups

The bot keeps its settings and moderation warnings in a SQLite database on a Docker volume.
Every update copies it into the `backups` folder first, and the `backup` action does the same at any time.
The folder keeps the last 7 copies, named after the time they were taken, such as `bot-2026-10-11-040000.db`.

The `restore` action lists the copies and asks which one to put back.
It backs up the current database before it replaces it, so a restore can be undone with another restore.
To move the bot to another computer, copy the `backups` folder along with `.env` and run `restore` there.

### Offline alerts

A heartbeat service can tell you when the bot goes offline, whether it crashed, lost its connection, or the computer shut down.
The bot reports to the service every 5 minutes while it is connected to Discord.
When the reports stop, the service sends you an email or a Discord message.
These steps use [healthchecks.io](https://healthchecks.io), which is free for a few bots.

1. Sign up at healthchecks.io and open your project.
2. Click **Add Check**. Name it after the bot, set **Period** to 5 minutes and **Grace Time** to 10 minutes, and save.
3. Copy the check's ping URL, such as `https://hc-ping.com/1f2e3d4c-...`. It works like a password, so keep it private.
4. Add it to `.env` as `HEARTBEAT_URL=` followed by the URL.
5. Run `run.bat` on Windows or `./run.sh` elsewhere, so the bot restarts with the setting.
6. On healthchecks.io, open **Integrations** to add a Discord channel or other ways to be told, next to the email that is on by default.

The check turns green within 5 minutes.
The service also alerts while the computer sleeps, because the bot is offline then too.

### Health check

While the bot is connected to Discord, it refreshes a small file every 30 seconds, and the Docker image's health check reads its age.
A bot that is stuck or lost its connection therefore shows as unhealthy in `run.bat status` and in Docker Desktop, not only one that crashed.
A new release that starts but never connects fails the update's check, so the update puts the previous version back.

### Development

Run the tests with `uv run pytest`.
Run every lint and format check with `uvx pre-commit run --all-files`, or install the hooks once with `uvx pre-commit install` so they run on each commit.
The coding, prose, and commit conventions are documented in [dev-standards](https://github.com/Lempki/dev-standards).

### Docker

Alternatively, you can run the bot as a Docker container.

1. Copy `.env.template` to `.env` and set `DISCORD_TOKEN`, `API_MORSHU_URL`, and `API_MORSHU_SECRET`. Inside the container, `localhost` is the container itself, so the URL must point at an address the container can reach.
2. Build and start the container:

   ```
   docker compose up -d --build
   ```

The container restarts automatically unless you stop it.
The database lives at `/app/data/bot.db` on the `bot-data` volume, so settings and warnings survive rebuilds and `docker compose down`.
Only `docker compose down -v` deletes it.

To also run api-morshu, clone it next to this repository and use the stack file instead:

```
docker compose -f compose.stack.yml up -d --build
```

Add `--profile media` to also run api-media, cloned next to this repository the same way. Set `API_MEDIA_SECRET` in `.env` first, because api-media refuses to start without a secret of at least 16 characters.
The stack builds each service from its sibling folder and connects them on a private network.
It also names each service's published image, which a downloaded release runs instead of building it.
It passes `API_MORSHU_SECRET`, and `API_MEDIA_SECRET` when the media profile is used, from this repository's `.env` to the matching service, so the bot and each service always agree.

With the media profile, api-media reads its own settings, such as `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`, `SPONSORBLOCK`, and `YDL_COOKIES_FILE`, from an optional `api-media.env` next to the stack file.
A Git clone can keep them in `../api-media/.env` instead, and `api-media.env` wins where both set the same setting.
Neither file is needed unless you change one of api-media's defaults, and api-media's README lists every setting.
For a YouTube cookies file, put it in a `cookies` folder next to the stack file, set `MEDIA_COOKIES_DIR=./cookies` in `.env`, and set `YDL_COOKIES_FILE=cookies/youtube.txt` in `api-media.env`.
The stack's fixed project name keeps the database on its own `bot-data` volume, whatever this folder is called.

Docker keeps at most two log files of 5 MB per container and overwrites the oldest.
The bot's container may use at most 512 MB of memory, and each api-* service in the stack 1 GB.
That is several times their normal use, so only a leak reaches it, and the container that leaks restarts on its own.

## Configuration

The base configuration variables are documented in the [discord-bot-template](https://github.com/Lempki/discord-bot-template) repository. The following variables are either specific to discord-bot-morshu or behave differently from the template defaults.

| Variable | Default | Description |
|---|---|---|
| `COGS_TO_LOAD` | `help` | Cogs to load at startup. `.env.template` sets `help,morshu`, which is this bot's default set. Use `help,voice,morshu` to add voice channel commands, or `help,voice,media,info,morshu,admin,moderation,events` for the full feature set. The `media` cog also needs `API_MEDIA_URL` and `API_MEDIA_SECRET`. |
| `LOCALE` | `silent` | The fallback language for users whose Discord language the bot does not speak. Built-in values are `en` and `fi`. `silent` mutes public replies to commands, such as generation progress and public error notices. Private replies, such as `/help`, admin and moderator replies, and private error messages, are still sent because only the person who ran the command sees them. |
| `API_MORSHU_URL` | Not set | Base URL of the api-morshu service. `.env.template` sets `http://localhost:8002`. Required when the `morshu` cog is loaded, and the bot stops at startup without it. `compose.stack.yml` overrides this inside the stack. |
| `API_MORSHU_SECRET` | Not set | Bearer token for the api-morshu service. Must match `API_SECRET` in the service configuration, which requires at least 16 characters. |
| `HEARTBEAT_URL` | Not set | The ping URL of a heartbeat service, such as healthchecks.io, which alerts you when the bot stops reporting that it is online. See [Offline alerts](#offline-alerts). |
| `UPDATE_WEBHOOK_URL` | Not set | A Discord webhook that hears when a nightly update installs a new release or fails. It works like a password. |

## Project structure

```
discord-bot-morshu/
├── bot.py               # Entry point.
├── config.py            # Reads settings and api-* service URLs from the environment.
├── localization.py      # This bot's own messages and translations, layered on the core ones.
├── cogs/
│   ├── help.py          # /help, a short guide to the bot's features, and /about.
│   ├── morshu.py        # Morshu TTS commands (/generate, /morshu).
│   ├── voice.py         # /voice join, leave, and stop. The bot leaves on its own when alone or idle.
│   ├── media.py         # /play, /music, and /queue, with a per-server queue and the now-playing panel.
│   ├── info.py          # /info server, member, and avatar.
│   ├── admin.py         # /admin command group, including /admin automod.
│   ├── moderation.py    # /warn, /warnings, /timeout, /untimeout, /kick, /ban, /purge, the right-click Warn and Report, and AutoMod escalation.
│   ├── events.py        # The auto-role and welcome message on join, and the goodbye message on leave.
│   └── template.py      # Reference cog inherited from discord-bot-template. Not loaded by default.
├── utils/
│   ├── audio.py         # MediaAPIClient, URL helpers, and audio sources for files, bytes, and streams.
│   ├── about.py         # Reads the bot's name, version, and repository link from pyproject.toml.
│   ├── automod.py       # Creates and edits the AutoMod rules that the bot owns.
│   ├── checks.py        # Command checks such as in_bot_channel(), and guild_of().
│   ├── database.py      # Versioned SQLite schema, per-guild settings, and warnings.
│   ├── heartbeat.py     # Reports to a heartbeat service while the bot is online.
│   ├── i18n.py          # Picks each user's language and translates command descriptions.
│   ├── moderation.py    # issue_warning(), shared by /warn and AutoMod escalation.
│   ├── replies.py       # respond() and finish(), which never leave a command "thinking".
│   ├── strings.py       # Every core message and command translation, in English and Finnish.
│   └── voice.py         # Joins, plays in, and leaves voice channels for every cog.
├── tests/               # Pytest suite. Runs in CI on pushes to main and on pull requests.
├── .env.template        # Template for environment variables.
├── pyproject.toml       # Project metadata and dependencies.
├── uv.lock              # Locked dependency versions.
├── ruff.toml            # Lint and format settings on top of the shared baseline.
├── setup.bat            # Windows setup script.
├── setup.sh             # macOS and Linux setup script.
├── scripts/bootstrap.py # The steps that both setup scripts run.
├── scripts/run.py       # The actions that both run scripts take.
├── run.bat              # Windows run script.
├── run.sh               # macOS and Linux run script.
├── Dockerfile
├── docker-compose.yml   # Runs the bot alone, with its database on a volume.
├── compose.stack.yml    # Runs the bot together with the api-* services it uses.
└── .dockerignore
```

## Staying in sync with the template

This repository does not maintain a git link to discord-bot-template.
Instead, discord-bot-template's `.template-manifest.toml` lists the core files that this bot keeps identical to it.
With both repositories cloned side by side, run this from this bot's directory to see which core files have drifted:

```bash
uvx --from git+https://github.com/Lempki/dev-standards@v0.5.0 dev-standards template-check --template ../discord-bot-template --diff
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
The core texts exist only in English and Finnish, so a new language also needs every core message in `BOT_TEXT` and every core command text in `BOT_COMMAND_TEXT`.

The tests list every message or command text a language is missing, and they fail on command texts longer than Discord's 100-character limit.

## Related services

The following services work alongside this bot and handle functionality that is managed centrally rather than bundled in each bot repository.
They are private, so a copy of this bot cannot run without access to api-morshu.

| Service | Description |
|---|---|
| api-morshu | Hosts the Morshu TTS engine. Accepts text and returns a synthesized WAV or video file. The source audio and sprite assets live here. |
| api-media | Resolves YouTube, SoundCloud, and Spotify track metadata, and streams their audio for playback. Bots call this instead of bundling yt-dlp directly. |

## Privacy and terms

The public Morshu follows its [privacy policy](PRIVACY.md) and [terms of service](TERMS.md).
In short, Morshu keeps none of the texts it speaks, stores nothing about members, and keeps only short technical logs.
Someone who runs their own copy is responsible for their own copy's privacy.

## License

This project is licensed under the [MIT License](LICENSE).
You may use, change, and share it, as long as every copy keeps the copyright notice and the license text.
