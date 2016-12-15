"""
Tests for functions maintaining interface compatibility
"""

from orb_api.api import orb_api, orb_resource, orb_resource_file, orb_resource_url
from orb_api.models import OrbResource, OrbResourceFile, OrbResourceURL


def test_orb_api():
    client = orb_api()

    base_url = 'http://localhost:9876'
    user_name = 'demo'
    api_key = '39b4043c69b8db27ddba761ba82479d00c8ccbb1'

    client.base_url = base_url
    client.user_name = user_name
    client.api_key = api_key

    assert client.base_url == base_url
    assert client.user_name == user_name
    assert client.api_key == api_key


def test_orb_resource():
    result = orb_resource()
    assert isinstance(result, OrbResource)

    result.title = "Alex Test9311"
    result.description = "something else to test with"
    assert result.title == "Alex Test9311"


def test_orb_resource_url():
    result = orb_resource_url()
    assert isinstance(result, OrbResourceURL)

    result.url = "http://www.wikipedia.org"
    assert result.url == "http://www.wikipedia.org"

def test_orb_resource_file():
    result = orb_resource_file()
    assert isinstance(result, OrbResourceFile)

    result.description = "Some file"
    assert result.description ==  "Some file"
