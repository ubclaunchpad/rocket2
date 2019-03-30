"""Test team command parsing."""
from command.commands.mention import MentionCommand
from unittest import TestCase, mock
from model.user import User

user = 'U123456789'
user2 = 'U234567891'

class MentionCommandTeset(TestCase):
    def setUp(self):
        """Set up test environment"""
        self.gh = mock.MagicMock()
        self.db = mock.MagicMock()
        self.sc = mock.MagicMock()
        self.testcommand = MentionCommand(self.db)
    
    def test_handle_no_input(self):
        """Test handle command
           with no additional args"""
        self.assertEqual(self.testcommand.handle('UFJ42EU67', user),
                         (self.testcommand.help, 200))
        
    def test_handle_add_karma_to_another_user(self):
        """Test handle command
           with kudos to another user"""
        user = User('U123456789')
        user.name = 'U123456789'
        self.db.retrieve.return_value = user
        self.assertEqual(self.testcommand.handle(('UFJ42EU67 ++'), user),
                         ("gave 1 karma to U123456789", 200))
    
    def test_handle_add_karma_to_self(self):
        """Test handle command
           with kudos to self"""
        self.assertEqual(self.testcommand.handle(("U123456789 ++"), user),
                         ("cannot give karma to self", 200))

    def test_handle_user_not_found(self):
        """Test handle command
           with kudos to unknown user"""
        self.db.retrieve.side_effect = LookupError
        self.assertEqual(self.testcommand.handle(f"{user2} ++", user),
                         (self.testcommand.lookup_error, 200))