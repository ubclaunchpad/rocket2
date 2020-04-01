"""Test iquit command parsing."""
from app.controller.command.commands import IQuitCommand
from app.model import User, Team, Permissions
from unittest import TestCase


def makeUser(slack, gid, guser, perm):
    """Make a user."""
    user = User(slack)
    user.github_id = gid
    user.github_username = guser
    user.permissions_level = perm
    return user


def makeTeam(ghid, leads_ghid, members_ghid):
    """Make a team."""
    team = Team(ghid, "COVID19", "Crime Stoppers")
    team.team_leads = team.team_leads.union(leads_ghid)
    team.members = team.members.union(members_ghid)
    return team


class TestFacade:
    """A testing facade that returns fake data."""

    def __init__(self):
        """Initialize with all the users/teams we need."""
        self.users = {
            "u1": makeUser("u1", "g1", "G1", Permissions.admin),
            "u2": makeUser("u2", "g2", "G2", Permissions.member),
            "u3": makeUser("u3", "g3", "G3", Permissions.team_lead),
            "u4": makeUser("u4", "g4", "G4", Permissions.member),
            "u5": makeUser("u5", "g5", "G5", Permissions.member),
            "u6": makeUser("u6", "g6", "G6", Permissions.member)
        }
        self.teams = {
            "t1": makeTeam("t1", [], []),
            "t2": makeTeam("t2", ["g1", "g3"], ["g1", "g2", "g3"]),
            "t3": makeTeam("t3", ["g1"], ["g1", "g4", "g2", "g5", "g6"]),
            "t4": makeTeam("t4", [], ["g6"])
        }

    def retrieve(self, Model, k):
        """Retrieve a model from the database."""
        if Model == User:
            return self.users.get(k)
        else:
            return self.teams.get(k)

    def query(self, Model, params=[]):
        """Query a table using a list of parameters."""
        db = self.users if Model == User else self.teams
        if len(params) == 0:
            return list(db.values())
        ret = []
        for param in params:
            if param[0] == "permission_level":
                ret.extend([o for o in db.values()
                            if str(o.permissions_level) == param[1]])
        return ret

    def query_or(self, Model, params=[]):
        """Query a table using a list of parameters."""
        db = self.users if Model == User else self.teams
        if len(params) == 0:
            return list(db.values())
        ret = []
        for param in params:
            if param[0] == "team_leads":
                ret.extend([o for o in db.values()
                            if param[1] in o.team_leads])
            if param[0] == "github_user_id":
                ret.extend([o for o in db.values()
                            if param[1] == o.github_id])
        return ret


class TestIQuitCommand(TestCase):
    """Test case for IQuitCommand class."""

    def setUp(self):
        """Set up the class and variables and whatnot."""
        self.facade = TestFacade()
        self.cmd = IQuitCommand(self.facade)

    def testReturnNoDuplicateUsers(self):
        """Test that users should see usernames once."""
        actual, resp = self.cmd.handle("", "u2")
        self.assertEqual(actual.count("u1"), 1)
        self.assertEqual(actual.count("u3"), 1)

    def testReturnNotEveryone(self):
        """Test that members should not see everyone."""
        actual, resp = self.cmd.handle("", "u6")
        print(actual)
        self.assertNotEqual(actual.count("u2"), 1)
        self.assertNotEqual(actual.count("u3"), 1)
        self.assertNotEqual(actual.count("u6"), 1)
