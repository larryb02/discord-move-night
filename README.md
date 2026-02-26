# Movie Night Bot

A Discord bot for organizing movie nights. Runs nomination and voting cycles, announces the winner, and resets for the next round.

## Features

- Nomination window where users submit movies
- Voting via Discord native polls
- Winner announcement with pin and voter tags
- Configurable nomination and voting durations

## Commands

| Command | Description |
|---|---|
| `/addmovie <title>` | Add a movie to the nomination list |
| `/movienight nomination_window:<duration> voting_window:<duration>` | Start a movie night cycle |

Durations use shorthand format: `30m`, `1h`, `2d`

## Setup

1. Clone the repo
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file:
    ```
    APP_TOKEN=your_bot_token
    GUILD_ID=your_guild_id
    ```
4. Run the bot: `python main.py`

## Requirements

- Python 3.11+
- `discord.py`
- Bot requires `Manage Messages` permission to pin announcements
