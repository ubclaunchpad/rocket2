"""Test the dynamodb interface (requires dynamodb running)."""
from unittest.mock import MagicMock
from unittest import TestCase
import pytest
import boto3

from app.model import User, Project, Team, Permissions
from config import Config
from tests.util import create_test_team, create_test_admin, create_test_project
from db.dynamodb import DynamoDB


class TestDDBConstants(TestCase):
    """For some reason the constants are also counted and thus tested."""

    def setUp(self):
        """Set up configurations for the constants."""
        self.config = MagicMock(Config)
        self.config.aws_users_tablename = 'users'
        self.config.aws_teams_tablename = 'teams'
        self.config.aws_projects_tablename = 'projects'
        self.const = DynamoDB.Const(self.config)

    def test_get_bad_table_name(self):
        """Test getting a bad table name by a bad type."""
        with self.assertRaises(TypeError):
            self.const.get_table_name(DynamoDB)

    def test_get_bad_key(self):
        """Test getting a bad primary key."""
        with self.assertRaises(TypeError):
            self.const.get_key('non-existent-table-id')

    def test_get_bad_set_attrs(self):
        """Test getting set attributes of a non-existent table."""
        with self.assertRaises(TypeError):
            self.const.get_set_attrs('non-existent-table-name')


class TestDynamoDB(TestCase):
    def setUp(self):
        self.config = MagicMock(Config)
        self.config.aws_users_tablename = 'users_test'
        self.config.aws_teams_tablename = 'teams_test'
        self.config.aws_projects_tablename = 'projects_test'
        self.config.aws_local = True
        self.ddb = DynamoDB(self.config)

    def tearDown(self):
        """Delete all database tables after usage."""
        # Delete the table itself instead of just the items in it
        botodb = boto3.resource(service_name="dynamodb",
                                region_name="",
                                aws_access_key_id="",
                                aws_secret_access_key="",
                                endpoint_url="http://localhost:8000")
        for table in botodb.tables.all():
            table.delete()

    @pytest.mark.db
    def test_store_invalid_type(self):
        """Test that we cannot store an object that isn't one of the types."""
        with self.assertRaises(RuntimeError):
            self.ddb.store(30)

    @pytest.mark.db
    def test_store_invalid_user(self):
        user = User('')
        self.assertFalse(self.ddb.store(user))

    @pytest.mark.db
    def test_store_invalid_team(self):
        team = Team('1', '', 'Brussel Sprouts')
        self.assertFalse(self.ddb.store(team))

    @pytest.mark.db
    def test_store_invalid_project(self):
        project = Project('12456', [''])
        project.github_urls = []
        self.assertFalse(self.ddb.store(project))

    @pytest.mark.db
    def test_store_same_users(self):
        """Test how database handles overwriting same user (same slack_id)."""
        user = create_test_admin('abc_123')
        user2 = create_test_admin('abc_123')
        user2.name = 'Sprouts'
        self.assertTrue(self.ddb.store(user))
        self.assertTrue(self.ddb.store(user2))

        self.assertEqual(self.ddb.retrieve(User, 'abc_123'), user2)

    @pytest.mark.db
    def test_store_retrieve_user(self):
        """Test to see if we can store and retrieve the same user."""
        user = create_test_admin('abc_123')

        success = self.ddb.store(user)
        another_user = self.ddb.retrieve(User, 'abc_123')

        self.assertTrue(success)
        self.assertEqual(user, another_user)

    @pytest.mark.db
    def test_store_retrieve_project(self):
        """Test to see if we can store and retrieve the same user."""
        urls = ['https://github.com/ubclaunchpad/rocket2']
        project = create_test_project('123456', urls)

        success = self.ddb.store(project)
        another_project = self.ddb.retrieve(Project, project.project_id)

        self.assertTrue(success)
        self.assertEqual(project, another_project)

    @pytest.mark.db
    def test_retrieve_invalid_user(self):
        """Test to see if we can retrieve a non-existant user."""
        with self.assertRaises(LookupError):
            self.ddb.retrieve(User, 'abc_123')

    @pytest.mark.db
    def test_retrieve_invalid_project(self):
        """Test to see if we can retrieve a non-existant user."""
        with self.assertRaises(LookupError):
            self.ddb.retrieve(Project, 'abc_123')

    @pytest.mark.db
    def test_query_user(self):
        """Test to see if we can store and query the same user."""
        user = create_test_admin('abc_123')
        self.assertTrue(self.ddb.store(user))
        users = self.ddb.query(User, [('permission_level', 'admin')])
        strict_users = self.ddb.query(User, [('permission_level', 'admin'),
                                             ('slack_id', 'abc_123')])
        all_users = self.ddb.query(User)
        self.assertEqual(user, users[0])
        self.assertEqual(user, all_users[0])
        self.assertEqual(user, strict_users[0])

    @pytest.mark.db
    def test_query_project(self):
        """Test to see if we can store and query the same project."""
        project = create_test_project('123456', ['abcd'])
        self.assertTrue(self.ddb.store(project))
        projects = self.ddb.query(Project, [('tags', 'python')])
        query = [('tags', 'python'),
                 ('tags', 'docker'),
                 ('display_name', 'Rocket2')]
        strict_projects = self.ddb.query(Project, query)
        all_projects = self.ddb.query(Project)

        self.assertEqual(project, projects[0])
        self.assertEqual(project, strict_projects[0])
        self.assertEqual(project, all_projects[0])

    @pytest.mark.db
    def test_retrieve_invalid_team(self):
        """Test to see if we can retrieve a non-existent team."""
        with self.assertRaises(LookupError):
            self.ddb.retrieve(Team, '1')

    @pytest.mark.db
    def test_update_user(self):
        """Test to see if we can update a user."""
        u = User('abc_123')
        self.assertTrue(self.ddb.store(u))

        u = self.ddb.retrieve(User, 'abc_123')
        u.name = 'Steven Universe'
        self.assertTrue(self.ddb.store(u))

        self.assertEqual(self.ddb.retrieve(User, 'abc_123').name,
                         'Steven Universe')

    @pytest.mark.db
    def test_update_team(self):
        """Test to see if we can update a team."""
        t = Team('1', 'brussel-sprouts', 'Brussel Sprouts')
        self.assertTrue(self.ddb.store(t))

        t = self.ddb.retrieve(Team, '1')
        t.add_member('abc_123')
        t.add_member('123_abc')
        self.assertTrue(self.ddb.store(t))

        self.assertEqual(len(self.ddb.retrieve(Team, '1').members), 2)

    @pytest.mark.db
    def test_store_retrieve_team(self):
        """Test to see if we can store and retrieve the same team."""
        team = create_test_team('1', 'rocket2.0', 'Rocket 2.0')
        self.assertTrue(self.ddb.store(team))
        another_team = self.ddb.retrieve(Team, '1')

        self.assertEqual(team, another_team)

    @pytest.mark.db
    def test_bulk_retrieve_no_users(self):
        uids = list(map(str, range(10)))
        self.assertEqual(self.ddb.bulk_retrieve(User, uids), [])

    @pytest.mark.db
    def test_bulk_retrieve_users(self):
        uids = list(map(str, range(10)))
        users = [create_test_admin(i) for i in uids]
        for user in users:
            self.assertTrue(self.ddb.store(user))

        retrieved_users = self.ddb.bulk_retrieve(User, uids)
        for user in retrieved_users:
            self.assertIn(user, users)

    @pytest.mark.db
    def test_query_or_teams(self):
        """Test edge cases like set inclusion in query_or."""
        teams = [create_test_team(str(i), "glob", "name") for i in range(10)]
        member_to_check = list(teams[0].members)[0]
        param = [('members', member_to_check)]
        for team in teams:
            self.assertTrue(self.ddb.store(team))
        queried_teams = self.ddb.query_or(Team, param)
        for team in teams:
            self.assertIn(team, queried_teams)

    @pytest.mark.db
    def test_query_or_users(self):
        uids = list(map(str, range(10)))
        users = [create_test_admin(i) for i in uids]

        for user in users[:5]:
            user.permissions_level = Permissions.member

        for user in users:
            self.assertTrue(self.ddb.store(user))

        params = [('slack_id', str(uid)) for uid in uids]
        queried_users = self.ddb.query_or(User, params)
        for user in queried_users:
            self.assertIn(user, users)

        params = [('permissions_level', lvl) for lvl in ['admin', 'member']]
        queried_users = self.ddb.query_or(User, params)
        for user in queried_users:
            self.assertIn(user, users)

    @pytest.mark.db
    def test_query_or_lotsa_users(self):
        uids = list(map(str, range(250)))
        users = [create_test_admin(i) for i in uids]

        # Bulk store to save on time
        table_name = self.ddb.CONST.get_table_name(User)
        table = self.ddb.ddb.Table(table_name)
        with table.batch_writer() as batch:
            for user in users:
                batch.put_item(Item=User.to_dict(user))

        params = [('slack_id', uid) for uid in uids]
        queried_users = self.ddb.query_or(User, params)
        self.assertCountEqual(queried_users, users)

    @pytest.mark.db
    def test_query_team(self):
        """Test to see if we can store and query the same team."""
        team = create_test_team('1', 'rocket2.0', 'Rocket 2.0')
        team2 = create_test_team('2', 'lame-o', 'Lame-O Team')
        team2.add_member('apple')
        self.assertTrue(self.ddb.store(team))
        self.assertTrue(self.ddb.store(team2))

        another_team = self.ddb.query(Team, [('display_name', 'Rocket 2.0')])
        same_team = self.ddb.query(Team, [('platform', 'slack')])
        multi_queries = self.ddb.query(Team, [('display_name', 'Rocket 2.0'),
                                              ('platform', 'slack')])
        member_team = self.ddb.query(Team, [('members', 'abc_123'),
                                            ('members', 'apple')])
        all_team = self.ddb.query(Team)

        self.assertEqual(team, another_team[0])
        self.assertEqual(team, all_team[0])
        self.assertEqual(team, same_team[0])
        self.assertEqual(team, multi_queries[0])
        self.assertEqual(team2, member_team[0])

    @pytest.mark.db
    def test_delete_user(self):
        user = create_test_admin('abc_123')
        self.assertTrue(self.ddb.store(user))

        self.assertEqual(len(self.ddb.query(User)), 1)
        self.ddb.delete(User, 'abc_123')
        self.assertEqual(len(self.ddb.query(User)), 0)

    @pytest.mark.db
    def test_delete_team(self):
        team = create_test_team('1', 'rocket-2.0', 'Rocket 2.0')
        self.assertTrue(self.ddb.store(team))

        self.assertEqual(len(self.ddb.query(Team)), 1)
        self.ddb.delete(Team, '1')
        self.assertEqual(len(self.ddb.query(Team)), 0)

    @pytest.mark.db
    def test_delete_project(self):
        project = create_test_project('abc_123', ['a'])
        self.assertTrue(self.ddb.store(project))

        self.assertEqual(len(self.ddb.query(Project)), 1)
        self.ddb.delete(Project, project.project_id)
        self.assertEqual(len(self.ddb.query(Project)), 0)
