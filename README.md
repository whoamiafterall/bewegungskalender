# Bewegungskalender2Telegram

This is a fork of https://gitlab.com/iexos/caldav2telegram.
This script fetches calendar events via caldav from a Nextcloud and posts them into a Telegram channel: https://t.me/bewegungskalender.

## Setup

This is a WIP, it should be installable via `pip` in the future.

You need to install the following python packages:

- `PyYAML` (tested with `v6`)
- `pytz`
- `caldav` (`>= 0.10.1`)
- `icalendar`
- optional: `python-telegram-bot` (tested with `v13`, needed for telegram output)

You need to create a config file. You can specify the path using `--config CONFIG_PATH` or use the default `config.yml`. You can find more information in `config.example.yml`.

### Setup Telegram

For the telegram output, you will need to setup a telegram bot:

* get a token first, see the [Telegram documentation](https://core.telegram.org/bots#how-do-i-create-a-bot)
* insert the token into your config file
* invite the bot into a channel
* run with `--get-telegram-updates` flag to get the id of that channel
  * you might get the update for being added to a channel only once! If you miss it, remove the bot from that channel and add it again
* insert the correct `group_id` into your config file

### Setup Signal

The Signal output uses [signal-cli](https://github.com/AsamK/signal-cli/) in the background. See its documentation on how to set it up and get the `group_id` using the `listGroups` command.

## Running

Run the script via

```
cd src
python3 -m post_caldav_events.main
```

To post regular updates, schedule it via cron or similar.

## Dev testing

This is a work in progress. You will need `pytest` and `podman-compose` to run tests.
