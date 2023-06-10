import os

import logging

import telebot

import models
import views

BOT_TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_TOKEN = os.environ.get('ADMIN_TOKEN')

DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_PORT = os.environ.get('DB_PORT', '5432')
DB_HOST = os.environ.get('DB_HOST', 'postgres_db')
LOGLEVEL = os.environ.get('LOGLEVEL')


# init bot
bot = telebot.TeleBot(BOT_TOKEN)
logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

# init database
logger.info('Initializing database...')
models.db.bind(provider='postgres', user=DB_USER, password=DB_PASSWORD,
               host=DB_HOST, port=DB_PORT, database=DB_NAME)
models.db.generate_mapping(create_tables=True)


# Bot helpers
def send(incoming_message: object, outcoming_message: str):
    """
    Send message (without Telegram reply wrapper).

    * incoming_message: the original message object
          came to bot from user
    * outcoming_message: answer the bot should send to
          the author of incoming_message
    """
    bot.send_message(
        incoming_message.from_user.id,
        outcoming_message,
        parse_mode='HTML'
    )


def reply(to_message: object, with_message: str):
    """
    Reply to given incoming message with outcoming message
    (with Telegram reply wrapper).

    * to_message: the original message object
          came to bot from user
    * with_message: answer the bot should send to
          the author of incoming_message
    """
    bot.reply_to(
            to_message,
            with_message,
            parse_mode='HTML'
        )


# Message handlers
@bot.message_handler(commands=['start', 'help'])
def answer_start(message):
    """
    Bot sends general help page and basic bot info
    """
    send(message, views.hello(message.from_user.username))


@bot.message_handler(commands=['answer'])
@models.db_session
def get_answer(message):
    """
    Bot saves new answer to puzzle
    """
    user_id = message.from_user.id
    user_name = message.from_user.username
    command: list = message.text[7:].strip().split()
    if not len(command) >= 2:
        err_txt = 'Please check your command, bad syntax!'
        reply(message, views.command_help(
            command='answer', error_text=err_txt)
        )
        return

    # puzzle checks
    puzzle_id: str = command[0]
    if not puzzle_id.isdigit():
        err_txt = (
            'Please check your command, bad syntax! '
            f'Puzzle ID should be a number, not {puzzle_id}'
        )
        reply(message, views.command_help(
            command='answer', error_text=err_txt)
        )
        return

    puzzle: models.Puzzle = models.Puzzle.exists(puzzle_id)
    if not puzzle:
        err_txt = (
            'Please check your command, bad syntax! '
            f'Puzzle ID should be a number, not {puzzle_id}'
        )
        reply(message, views.error(
            error_text=f'No puzzle with ID {puzzle_id}'
            )
        )
        return

    # user checks
    user_answer: models.Answer | None = (
        models.Puzzle.user_has_answer(user_id, puzzle_id)
    )
    if user_answer:
        err_txt = (
            f'You have already answered this puzzle #{puzzle_id}: '
            f'({user_answer.registered})!'
        )
        reply(message, views.error(error_text=err_txt))
        return

    # user answer checks
    user_answer: str = ' '.join(command[1:])
    if len(user_answer) < 6:
        err_txt = (
            f'Your answer seems too short: {user_answer}'
        )
        reply(message, views.command_help(
            command='answer', error_text=err_txt)
        )
        return
    elif len(user_answer) > 100:
        err_txt = (
            f'Your answer seems too big: {len(user_answer)} symbols! '
        )
        reply(message, views.error(error_text=err_txt))
        return
    elif user_answer.isdigit():
        err_txt = (
            f'Your answer is just a number: {user_answer}'
        )
        reply(message, views.command_help(
            command='answer', error_text=err_txt)
        )
        return
    elif any([el in user_answer for el in '#$&^<>']):
        err_txt = (
            'Please do not use #$&^&gt;&lt; symbols in your answer.'
        )
        reply(message, views.error(error_text=err_txt))
        return

    # if all checks ok:
    try:
        answer = puzzle.register_new_answer(
            user_id=user_id,
            answer=user_answer,
            username=user_name,
        )
    except Exception as exc:
        reply(message, views.error(exc))
    else:
        send(message, views.got_answer(answer=answer,
                                       username=user_name,
                                       puzzle=puzzle))


@bot.message_handler(commands=['show'])
@models.db_session
def show_answers(message):
    """
    Bot shows players' answers to puzzle
    """
    user_id = message.from_user.id
    user_name = message.from_user.username
    command: list = message.text[5:].strip().split()
    if len(command) != 2:
        err_txt = 'Please check your command, bad syntax!'
        reply(message, views.command_help(
            command='show', error_text=err_txt)
        )
        return
    puzzle_id, token = command

    # puzzle_id checks
    if not puzzle_id.isdigit():
        err_txt = (
            'Please check your command, bad syntax! '
            f'Puzzle ID should be a number, not {puzzle_id}'
        )
        reply(message, views.command_help(
            command='answer', error_text=err_txt)
        )
        return
    if not models.Puzzle.exists(puzzle_id):
        err_txt = (
            'Please check your command, bad syntax! '
            f'Puzzle ID should be a number, not {puzzle_id}'
        )
        reply(message, views.error(
            error_text=f'No puzzle with ID {puzzle_id}'
            )
        )
        return

    if token != ADMIN_TOKEN:
        logger.error(
            f'User {user_id} (name: {user_name}) tried to get answers '
            f'for puzzle No {puzzle_id}, but used bad ADMIN_TOKEN.'
        )
        err_txt = (
            f'Authentication error. Your token {token} is not valid'
        )
        reply(message, views.error(error_text=err_txt))
        return
    try:
        puzzle = models.Puzzle.get(id=puzzle_id)
    except Exception as exc:
        reply(message, views.error(error_text=exc))
    else:
        reply(message, views.show_answers(puzzle=puzzle))


@bot.message_handler(commands=['register'])
@models.db_session
def register_puzzle(message):
    """
    Bot registers new puzzle and gives back id
    """
    user_id = message.from_user.id
    user_name = message.from_user.username
    command: list = message.text[9:].strip().split()
    if not len(command) >= 2:
        err_txt = 'Please check your command, bad syntax!'
        reply(message, views.command_help(
            command='register', error_text=err_txt)
        )
        return
    token = command.pop()
    if token != ADMIN_TOKEN:
        logger.error(
            f'User {user_id} (name: {user_name}) tried to register '
            f'a puzzle, but used bad ADMIN_TOKEN.'
        )
        err_txt = (
            f'Authentication error. Your token {token} is not valid'
        )
        reply(message, views.error(error_text=err_txt))
        return
    puzzle_name: str = ' '.join(command)
    if len(puzzle_name) > 100:
        err_txt = (
            f'The name for your puzzle is too long: {len(puzzle_name)}'
        )
        reply(message, views.command_help(
            command='register', error_text=err_txt)
        )
        return
    elif any([el in puzzle_name for el in '#$&^<>']):
        err_txt = (
            'Please do not use #$&^&gt;&lt; symbols '
            'in your puzzle name.'
        )
        reply(message, views.error(error_text=err_txt))
        return
    try:
        puzzle = models.Puzzle(name=puzzle_name)
        models.commit()
    except Exception as exc:
        reply(message, views.error(error_text=exc))
    else:
        logger.info(f'Registered new puzzle, id: {puzzle.id}')
        reply(message, views.got_puzzle(puzzle=puzzle))


# Service functions
def run_long_polling():
    logger.info('Starting polling...')
    bot.infinity_polling(skip_pending=True)


if __name__ == '__main__':
    run_long_polling()
