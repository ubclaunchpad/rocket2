"""Contain the handlers for each type of supported GitHub webhook."""
import app.controller.webhook.github.events.membership as membership
import app.controller.webhook.github.events.organization as organization
import app.controller.webhook.github.events.team as team

MembershipEventHandler = membership.MembershipEventHandler
OrganizationEventHandler = organization.OrganizationEventHandler
TeamEventHandler = team.TeamEventHandler
