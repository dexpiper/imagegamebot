# ImaginAerium Telegram Game Bot

This bot helps to play ImaginAerium (https://t.me/imaginaiarium) Telegram game. It stores players' answers to puzzles and shows them to admins.

### Technologies and libraries

* Python 3.10
* [pyTelegramBotAPI 4.12.0](https://github.com/eternnoir/pyTelegramBotAPI)
* PonyORM 0.7.16 & Postgres
* Jinja2

### Deploy

It is as simple as this:

`$ git clone <> && cd imagegamebot`
`$ docker-compose up --build -d`

Also you should define variables in .env file in the ./imagegamebot or directly in docker-compose.yaml:

* BOT_TOKEN -- _token from BotFather_
* ADMIN_TOKEN -- _token that your admins will use inside the bot_
* DB_PASSWORD -- _password for your Postgres database_
* DB_NAME=imagegamebot
* DB_USER=imagegamebot
* LOGLEVEL -- _use debug for verbose logs or info_