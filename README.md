# TfL Telegram Bot

Telegram bot that interacts with TfL (Transport for London) API. Try it
[here](https://telegram.me/mike_tfl_bot).

## Installation

Be sure to register your bot on Telegram to get a token.

Store that token in a file called `token` to be read by the program.

Build a Docker image with:

```
$ docker build -t tfl-bot .
```

Run with:

```
$ docker run -d --name tfl-bot tfl-bot
```
