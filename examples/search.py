import argparse
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_PATH = os.path.normpath(os.path.join(BASE_DIR, '..', 'orb_api'))

if PROJECT_PATH not in sys.path:
    sys.path.append(PROJECT_PATH)

from api import orb_api


def run(query):
    api = orb_api()
    api.base_url = 'http://localhost:8000'
    api.user_name = 'demo'
    api.api_key = '39b4043c69b8db27ddba761ba82479d00c8ccbb1'
    results = api.search(query)
    for result in results['objects']:
        print(result['title'])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("query", help="Search term")
    args = parser.parse_args()
    run(args.query)