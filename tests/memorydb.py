from db.facade import DBFacade
from app.model import User, Team, Project, Permissions
from typing import TypeVar, List, Type, Tuple, cast, Set

T = TypeVar('T', User, Team, Project)


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


PROJ_ATTRS = {
    'project_id': 'project_id',
    'github_urls': 'github_urls',
    'github_team_id': 'github_team_id',
    'display_name': 'display_name',
    'short_description': 'short_description',
    'long_description': 'long_description',
    'tags': 'tags',
    'website_url': 'website_url',
    'appstore_url': 'appstore_url',
    'playstore_url': 'playstore_url'
}


def field_is_set(Model: Type[T], field: str) -> bool:
    if Model is Team:
        return field in ['team_leads', 'members']
    elif Model is Project:
        return field in ['tags', 'github_urls']
    else:
        return False


def field_to_attr(Model: Type[T], field: str) -> str:
    if Model is User:
        return USER_ATTRS[field]
    elif Model is Team:
        return TEAM_ATTRS[field]
    elif Model is Project:
        return PROJ_ATTRS[field]
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
    elif isinstance(m, Project):
        return cast(Project, m).project_id


class MemoryDB(DBFacade):
    def __init__(self,
                 users: List[User] = [],
                 teams: List[Team] = [],
                 projs: List[Project] = []):
        self.users = {u.slack_id: u for u in users}
        self.teams = {t.github_team_id: t for t in teams}
        self.projs = {p.project_id: p for p in projs}

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
