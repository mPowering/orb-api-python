#!/usr/bin/python
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_PATH = os.path.normpath(os.path.join(BASE_DIR, '..', 'orb_api'))

if PROJECT_PATH not in sys.path:
    sys.path.append(PROJECT_PATH)

from api import orb_api, orb_resource


def run():
    api = orb_api()
    api.base_url = 'http://localhost:8000'
    api.user_name = 'demo'
    api.api_key = '39b4043c69b8db27ddba761ba82479d00c8ccbb1'

    resource = orb_resource()
    resource.title = "Alex Test9311"
    resource.description = "something else to test with"

    id = api.add_resource(resource)
    if id:
        api.add_resource_image(id,'/home/alex/temp/image.jpg')



if __name__ == "__main__":
    run()