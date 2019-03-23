"""Test the data model for a project."""
from model import Project


def test_valid_project():
    """Test the Project static method is_valid()."""
    p = Project('12345', ['https://www.github.com/ubclaunchpad/rocket2'])
    assert Project.is_valid(p)


def test_project_getters_and_setters():
    """Test project getters and setters methods."""
    p = Project('12345', ['http://www.github.com/ubclaunchpad/rocket'])

    assert isinstance(p.project_id, str)
    assert p.github_team_id == '12345'
    assert p.github_urls == ['http://www.github.com/ubclaunchpad/rocket']

    project_id = 'abcdef1234'
    team_id = '123456'
    github_urls = ['https://www.github.com/ubclaunchpad/rocket2']
    display_name = 'UBC Launch Pad'
    short_description = 'UBC Launch Pad is a UBC club'
    long_description = 'UBC Launch Pad is a UBC software engineering club'
    tags = ['c++', 'java', 'big-no']
    website_url = 'https://www.github.com/ubclaunchpad'
    medium_url = 'https://www.medium.com/'
    appstore_url = 'https://www.placeholder.com'
    playstore_url = 'https://www.google.jp'

    p.project_id = project_id
    p.github_team_id = team_id
    p.github_urls = github_urls
    p.display_name = display_name
    p.short_description = short_description
    p.long_description = long_description
    p.tags = tags
    p.website_url = website_url
    p.medium_url = medium_url
    p.appstore_url = appstore_url
    p.playstore_url = playstore_url

    assert p.project_id == project_id
    assert p.github_team_id == team_id
    assert p.github_urls == github_urls
    assert p.display_name == display_name
    assert p.short_description == short_description
    assert p.long_description == long_description
    assert p.tags == tags
    assert p.website_url == website_url
    assert p.medium_url == medium_url
    assert p.appstore_url == appstore_url
    assert p.playstore_url == playstore_url


def test_project_equalities():
    """Test project __eq__ and __ne__ methods."""
    p0 = Project('12345', ['https://www.github.com/'])
    p1 = Project('12345', ['https://www.github.com/'])
    p2 = Project('1234', ['https://www.github.com/'])

    assert p0 != p1
    assert p0 != p2
    assert p1 != p2

    p0.project_id = 'abc123'
    p1.project_id = 'abc123'

    assert p0 == p1
    assert p0 != p2
    assert p1 != p2
