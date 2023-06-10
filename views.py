from datetime import datetime

from jinja2 import Environment, PackageLoader, select_autoescape

from unicode import emoji


# setting Jinja2-specified params
env = Environment(
        loader=PackageLoader('views'),
        autoescape=select_autoescape()
    )
env.trim_blocks = True
env.lstrip_blocks = True


def format_datetime(value: datetime,
                    format_string: str):
    return value.strftime(format_string)


env.filters['format_datetime'] = format_datetime


def hello(username: str):
    """
    Render basic hello template
    """
    with open('version.txt', 'r') as fd:
        ver = fd.read()
    template = env.get_template("hello.jinja2")
    return template.render(username=username, version=ver, emoji=emoji)


def command_help(command: str, error_text: str = ''):
    """
    Send help message about certain command
    """
    template = env.get_template(f"commands/{command}.jinja2")
    return template.render(error_text=error_text, emoji=emoji)


def error(error_text: str):
    """
    Render error_text into a standard error template
    """
    template = env.get_template("error.jinja2")
    return template.render(error_text=error_text, emoji=emoji)


def got_answer(answer, username, puzzle):
    """
    Render got_answer template
    """
    template = env.get_template("gotanswer.jinja2")
    return template.render(answer=answer, username=username,
                           puzzle=puzzle, emoji=emoji)


def got_puzzle(puzzle):
    """
    Render got_puzzle template
    """
    template = env.get_template("gotpuzzle.jinja2")
    return template.render(puzzle=puzzle, emoji=emoji)


def show_answers(puzzle):
    """
    Render show_answers template
    """
    template = env.get_template("showanswers.jinja2")
    return template.render(puzzle=puzzle, emoji=emoji)
