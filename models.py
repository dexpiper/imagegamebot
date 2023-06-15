from pony.orm import Database
from pony.orm import Required, Optional, Set
from pony.orm import select, commit, db_session  # noqa: F401
from pony.orm.core import ObjectNotFound

from datetime import datetime, timedelta

db = Database()


class Answer(db.Entity):
    user_id = Required(int, size=64)
    username = Optional(str)
    text = Required(str, max_len=150)
    registered = Required(datetime, default=datetime.now)
    puzzle = Required('Puzzle')

    @classmethod
    def get_recent(cls):
        return select(
            a for a in Answer
            if a.registered >= datetime.now() - timedelta(hours=24)
        )


class Puzzle(db.Entity):
    answers = Set(Answer)
    name = Optional(str, max_len=150)

    @classmethod
    def exists(cls, puzzle_id: int) -> bool:
        try:
            return cls[puzzle_id]
        except ObjectNotFound:
            return False

    @classmethod
    def user_has_answer(cls,
                        user_id: int,
                        puzzle_id: int) -> bool:
        with db_session:
            p = cls[puzzle_id]
            q = select(a for a in p.answers if a.user_id == user_id)
            return q.first() if q else False

    def register_new_answer(self, user_id: int, answer: str,
                            username: str = None):
        """
        Register new answer to a puzzle
        """
        with db_session:
            Answer(user_id=user_id,
                   text=answer,
                   username=username,
                   puzzle=self)
            commit()
