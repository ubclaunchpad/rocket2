"""Represent a data model for a Slack event."""
import json


class SlackEvent:
    """Represent a Slack event with related fields and methods."""

    __json_string = ""
    __token = ""
    __team_id = ""
    __api_app_id = ""
    __type = ""
    __authed_users = []
    __event_id = ""
    __event_time = 0
    __event_obj = ""
    __event_type = ""

    def __init__(self, json_string):
        """Create the event with the fields specified by the JSON string."""
        self.__json_string = json_string
        json_obj = json.loads(json_string)
        self.__token = json_obj["token"]
        self.__team_id = json_obj["team_id"]
        self.__api_app_id = json_obj["api_app_id"]
        self.__type = json_obj["type"]
        self.__authed_users = json_obj["authed_users"]
        self.__event_id = json_obj["event_id"]
        self.__event_time = json_obj["event_time"]
        self.__event_obj = json_obj["event"]
        __event_type = self.__event_obj["type"]

    def deserialize(self):
        """Return this Slack Event's JSON string representation."""
        return self.__json_string

    def get_event_attr(self, event_attr):
        """Return the field in the event with the given event attribute."""
        return self.__event_obj[event_attr]

    def get_token(self):
        """Return this Slack Event's token."""
        return self.__token

    def get_team_id(self):
        """Return this Slack Event's team ID."""
        return self.__team_id

    def get_api_app_id(self):
        """Return this Slack Event's API app ID."""
        return self.__api_app_id

    def get_type(self):
        """Return the type of callback associated with this Slack Event."""
        return self.__type

    def get_authed_users(self):
        """Return an array of IDs of users who see the Slack Event."""
        return self.__authed_users

    def get_event_id(self):
        """Return the event ID associated with this Slack Event."""
        return self.__event_id

    def get_event_time(self):
        """Return the epoch timestamp of when this Slack Event occured."""
        return self.__event_time

    def get_event_obj(self):
        """Return the inner event object of the Slack Event as a dictionary."""
        return self.__event_obj

    def get_event_type(self):
        """Return the event type of this Slack Event."""
        return self.__event_type
