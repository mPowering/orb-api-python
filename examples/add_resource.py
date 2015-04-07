#!/usr/bin/python
import os, sys
import MySQLdb

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_PATH = os.path.normpath(os.path.join(BASE_DIR, '..', 'mpower_api'))

if PROJECT_PATH not in sys.path:
    sys.path.append(PROJECT_PATH)

from api import mpower_api, mpower_resource, mpower_resource_file, mpower_resource_url


def run(): 
    api = mpower_api()
    api.base_url = 'http://localhost:8000'
    api.user_name = 'demo'
    api.api_key = '39b4043c69b8db27ddba761ba82479d00c8ccbb1'
        
    resource = mpower_resource()
    resource.title = "Alex Test9311"
    resource.description = "something else to test with"
    
    id = api.add_resource(resource)
    if id:
        api.add_resource_image(id,'/home/alex/temp/image.jpg')
    
    
    
if __name__ == "__main__":
    run() 