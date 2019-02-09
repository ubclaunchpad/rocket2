# Database Reference

## `users` Table

The `users` table stores all the users. With DynamoDB, we only need to specify a
fixed attribute to be the primary index. In this case, the user's `slack_id` is
the primary index. All other attributes are specified in the `model/user.py`
file, and are also listed here:

Attribute Name | Description
---|---
`slack_id` | `String`; The user's slack id
`email` | `String`; The user's email address
`github` | `String`; The user's Github handler
`github_user_id` | `String`; The user's Github user ID
`major` | `String`; The subject major the user is in
`position` | `String`; The user's position in _Launch Pad_
`bio` | `String`; A short (auto)biography
`image_url` | `String`; The user's avatar image URL
`permission_level` | `String`; The user's permission level

The user's permission level is one of [`member`, `admin`, `team_lead`].

## `teams` Table

The `teams` table stores all teams where `github_team_id` is the primary index.
All other attributes are specified in the `model/team.py` file, and are also
listed here:

Attribute Name | Description
---|---
`github_team_id` | `String`; The team's Github ID
`github_team_name` | `String`; The team's Github name
`display_name` | `String`; The teams's display
`platform` | `String`; The team's working platform
`members` | `String Set`; The team's set of members' Github IDs

## `projects` Table

The `projects` table stores all projects where `project_id` is the primary
index. All other attributes are specified in the `model/project.py` file, and
are also listed here:

Attribute Name | Description
---|---
`project_id` | `String`; The project's unique SHA1 ID, salted with a timestamp
`github_team_id` | `String`; The team's Github ID associated with the project
`github_urls` | `String Set`; A set of URLs pointing to project repositories
`display_name` | `String`; A name for the project
`short_description` | `String`; A short description that outlines the project
`long_description` | `String`; A longer and more in-depth description
`tags` | `String Set`; A set of tags taken from the Github repositories
`website_url` | `String`; A URL to the project's website
`medium_url` | `String`; A URL to the project's medium page
`appstore_url` | `String`; A URL to the project's Apple Appstore page
`playstore_url` | `String`; A URL to the project's Google Playstore page
