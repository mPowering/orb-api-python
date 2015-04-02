
import os, sys


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_PATH = os.path.normpath(os.path.join(BASE_DIR, '..', 'mpower_api'))

if PROJECT_PATH not in sys.path:
    sys.path.append(PROJECT_PATH)

from api import mpower_api


def run(): 
    api = mpower_api()
    api.base_url = 'http://localhost:8000'
    api.user_name = 'demo'
    api.api_key = '39b4043c69b8db27ddba761ba82479d00c8ccbb1'
    
    
    
if __name__ == "__main__":
    run() 