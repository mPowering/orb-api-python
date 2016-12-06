#!/usr/bin/env python

# -*- coding: utf-8 -*-

import argparse
from orb_api.api import OrbClient


def main():
    """
    Allows basic command line access of an ORB via the API over the command lint

    """

    parser = argparse.ArgumentParser(description="Run API utility functions.")
    parser.add_argument("command")
    parser.add_argument("--host", dest="host", default="http://localhost:8000",
                   help="The host on which to operate against (default: http://localhost:8000)")
    parser.add_argument("--username", dest="username", help="Username for the API", required=True),
    parser.add_argument("--key", dest="api_key", help="Users API key", required=True)
    parser.add_argument("--sleep", dest="sleep", type=int, default=1, help="Sleep per request duration")
    args = parser.parse_args()

    client = OrbClient(args.host, args.username, args.api_key, sleep=args.sleep)

    if args.command == "list":
        count, results = client.list_resources()
        print("There are {} total resources returned.\n".format(count))

        for obj in results:
            print(u"{}\n{}\n".format(obj['title'], obj['url']))


if __name__ == "__main__":
    main()
