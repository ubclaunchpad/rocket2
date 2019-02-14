"""Test the data model for a project."""
from model.project import Project


def test_valid_project():
    """Test the Project static method is_valid()."""
    p = Project('12345', ['https://www.github.com/ubclaunchpad/rocket2'])
    assert Project.is_valid(p)


def test_project_getters_and_setters():
    """Test project getters and setters methods."""
    p = Project('12345', ['http://www.github.com/ubclaunchpad/rocket'])

    assert isinstance(p.get_project_id(), str)
    assert p.get_project_id().isalnum()
    assert p.get_github_team_id() == '12345'
    assert p.get_github_urls() == ['http://www.github.com/ubclaunchpad/rocket']

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

    p.set_project_id(project_id)
    p.set_github_team_id(team_id)
    p.set_github_urls(github_urls)
    p.set_display_name(display_name)
    p.set_short_description(short_description)
    p.set_long_description(long_description)
    p.set_tags(tags)
    p.set_website_url(website_url)
    p.set_medium_url(medium_url)
    p.set_appstore_url(appstore_url)
    p.set_playstore_url(playstore_url)

    assert p.get_project_id() == project_id
    assert p.get_github_team_id() == team_id
    assert p.get_github_urls() == github_urls
    assert p.get_display_name() == display_name
    assert p.get_short_description() == short_description
    assert p.get_long_description() == long_description
    assert p.get_tags() == tags
    assert p.get_website_url() == website_url
    assert p.get_medium_url() == medium_url
    assert p.get_appstore_url() == appstore_url
    assert p.get_playstore_url() == playstore_url


def test_project_equalities():
    """Test project __eq__ and __ne__ methods."""
    p0 = Project('12345', ['https://www.github.com/'])
    p1 = Project('12345', ['https://www.github.com/'])
    p2 = Project('1234', ['https://www.github.com/'])

    assert p0 != p1
    assert p0 != p2
    assert p1 != p2

    p0.set_project_id('abc123')
    p1.set_project_id('abc123')

    assert p0 == p1
    assert p0 != p2
    assert p1 != p2
