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
    
    '''
    db = MySQLdb.connect(host="localhost", # your host, usually localhost
                     user="john", # your username
                      passwd="megajonhy", # your password
                      db="dc_") # name of the data base

    # you must create a Cursor object. It will let
    #  you execute all the queries you need
    cur = db.cursor() 
    
    # Use all the SQL you like
    cur.execute("SELECT * FROM YOUR_TABLE_NAME")
    
    # print all the first cell of all the rows
    for row in cur.fetchall() :
        print row[0]
    '''
    
    resource = mpower_resource()
    resource.title = "Alex Test931"
    resource.description = "something else to test with"
    
    id = api.add_resource(resource)
    api.add_resource_image(id,'/home/alex/temp/image.jpg')
    
    
if __name__ == "__main__":
    run() 