from db.facade import DBFacade
from app.model import User, Team, Permissions
from typing import TypeVar, List, Type, Tuple, cast, Set

T = TypeVar('T', User, Team)


# Convert DB field names to python attribute names
USER_ATTRS = {
    'slack_id': 'slack_id',
    'permission_level': 'permissions_level',
    'email': 'email',
    'name': 'name',
    'github': 'github_username',
    'github_user_id': 'github_id',
    'major': 'major',
    'position': 'position',
    'bio': 'biography',
    'image_url': 'image_url',
    'karma': 'karma'
}


TEAM_ATTRS = {
    'github_team_id': 'github_team_id',
    'github_team_name': 'github_team_name',
    'display_name': 'display_name',
    'platform': 'platform',
    'members': 'members',
    'team_leads': 'team_leads'
}


def field_is_set(Model: Type[T], field: str) -> bool:
    if Model is Team:
        return field in ['team_leads', 'members']
    else:
        return False


def field_to_attr(Model: Type[T], field: str) -> str:
    if Model is User:
        return USER_ATTRS[field]
    elif Model is Team:
        return TEAM_ATTRS[field]
    return field


def filter_by_matching_field(ls: List[T],
                             Model: Type[T],
                             field: str,
                             v: str) -> List[T]:
    r = []
    is_set = field_is_set(Model, field)
    attr = field_to_attr(Model, field)

    # Special case for handling permission levels
    if attr == 'permissions_level':
        v = Permissions[v]  # type: ignore

    for x in ls:
        if is_set and v in getattr(x, attr):
            r.append(x)
        elif not is_set and v == getattr(x, attr):
            r.append(x)
    return r


def get_key(m: T) -> str:
    if isinstance(m, User):
        return cast(User, m).slack_id
    elif isinstance(m, Team):
        return cast(Team, m).github_team_id


class MemoryDB(DBFacade):
    """
    An in-memory database.

    To be used only in testing. **Do not attempt to use it in production.**
    Used when a test requires a database, but when we aren't specifically
    testing database functionalities.

    **Stored objects can be mutated by external references if you don't drop
    the reference after storing.**
    """

    def __init__(self,
                 users: List[User] = [],
                 teams: List[Team] = []):
        """
        Initialize with lists of objects.

        :param users: list of users to initialize the db
        :param teams: list of teams to initialize the db
        """
        self.users = {u.slack_id: u for u in users}
        self.teams = {t.github_team_id: t for t in teams}

    def get_db(self, Model: Type[T]):
        if Model is User:
            return self.users
        elif Model is Team:
            return self.teams
        raise LookupError(f'Unknown model {Model}')

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
        d = list(self.get_db(Model).values())
        for field, val in params:
            d = filter_by_matching_field(d, Model, field, val)
        return d

    def query_or(self,
                 Model: Type[T],
                 params: List[Tuple[str, str]] = []) -> List[T]:
        if len(params) == 0:
            return self.query(Model)

        d = list(self.get_db(Model).values())
        r: Set[T] = set()
        for field, val in params:
            r = r.union(set(filter_by_matching_field(d, Model, field, val)))
        return list(r)

    def delete(self, Model: Type[T], k: str):
        d = self.get_db(Model)
        if k in d:
            d.pop(k)
