from db.facade import DBFacade
from app.model import User, Team, Project  # , Permissions
from typing import Dict, TypeVar, List, Type, Tuple, cast

T = TypeVar('T', User, Team, Project)


def get_key(m: T) -> str:
    if isinstance(m, User):
        return cast(User, m).slack_id
    elif isinstance(m, Team):
        return cast(Team, m).github_team_id
    elif isinstance(m, Project):
        return cast(Project, m).project_id


class MemoryDB(DBFacade):
    def __init__(self,
                 users: Dict[str, User] = {},
                 teams: Dict[str, Team] = {},
                 projs: Dict[str, Project] = {}):
        self.users = dict(users)
        self.teams = dict(teams)
        self.projs = dict(projs)

    def get_db(self, Model: Type[T]):
        if Model is User:
            return self.users
        elif Model is Team:
            return self.teams
        elif Model is Project:
            return self.projs
        return {}

    def store(self, obj: T) -> bool:
        Model = obj.__class__
        if Model.is_valid(obj):
            key = get_key(obj)
            self.get_db(Model)[key] = obj
            return True
        return False

    def retrieve(self, Model: Type[T], k: str) -> T:
        d = self.get_db(Model)
        if k in d:
            return cast(T, d[k])
        else:
            raise LookupError(f'{Model.__name__}(id={k}) not found')

    def bulk_retrieve(self,
                      Model: Type[T],
                      ks: List[str]) -> List[T]:
        r = []
        for k in ks:
            try:
                m = self.retrieve(Model, k)
                r.append(m)
            except LookupError:
                pass
        return r

    def query(self,
              Model: Type[T],
              params: List[Tuple[str, str]] = []) -> List[T]:
        pass

    def query_or(self,
                 Model: Type[T],
                 params: List[Tuple[str, str]] = []) -> List[T]:
        pass

    def delete(self, Model: Type[T], k: str):
        pass
