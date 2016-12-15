#!/usr/bin/python
import argparse
import csv
import json
import os, sys
import urllib
import urllib2

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_PATH = os.path.normpath(os.path.join(BASE_DIR, '..', 'orb_api'))

if PROJECT_PATH not in sys.path:
    sys.path.append(PROJECT_PATH)
    
from api import orb_api, orb_resource, orb_resource_file, orb_resource_url, ORBAPIResourceExistsException
from error_codes import * 
   
INFILE = os.path.join(BASE_DIR, 'zika_data', 'Zika-ORB-data.csv')


CSV_FORMAT = {
              'title': 0,
              'organisation': 1,
              'description': 2,
              'resource-type': 3, 
              'license': 4,
              'health-domain': 5,
              'audience': 6,
              'geography': 7,
              'English': 8,
              'Spanish': 9,
              'Portuguese':10
              }


DEBUG = True


def run(orb_url, orb_username, orb_key): 
    api = orb_api()
    api.base_url = orb_url
    api.user_name = orb_username
    api.api_key = orb_key  
    api.verbose_output = DEBUG  
    
    with open(INFILE, 'rb') as csvfile:
        file_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for counter, row in enumerate(file_reader):
            # skip first row as has the headings
            if counter == 0:
                continue
            
            # skip if no title
            if row[CSV_FORMAT['title']].strip() == "":
                continue
            
            resource = orb_resource()
            resource.title =  row[CSV_FORMAT['title']]
            
            # get the video id 
            youtube_link = None
            LANGUAGES = []
            if row[CSV_FORMAT['English']].strip() != "":
                youtube_link = row[CSV_FORMAT['English']].strip()
                LANGUAGES.append("English")
            if row[CSV_FORMAT['Spanish']].strip() != "":
                youtube_link = row[CSV_FORMAT['Spanish']].strip()
                LANGUAGES.append("Spanish")
            if row[CSV_FORMAT['Portuguese']].strip() != "":
                youtube_link = row[CSV_FORMAT['Portuguese']].strip()
                LANGUAGES.append("Portuguese")
                
            if youtube_link: 
                
                youtube_link = youtube_link.split('/')
                video_id = youtube_link[len(youtube_link)-1]
                
                resource.description = row[CSV_FORMAT['description']].decode('utf-8') + '<div style="text-align:center;">' +\
                             '<iframe width="560" height="315" src="https://www.youtube.com/embed/'+\
                              video_id +\
                              '?rel=0&html5=1" frameborder="0" allowfullscreen></iframe></div>'
                              
                # get resource image from YouTube             
                image_file_path = os.path.join('/tmp', video_id + '.jpg')
                if not os.path.exists(image_file_path):
                    urllib.urlretrieve ("http://img.youtube.com/vi/%s/mqdefault.jpg" % (video_id), image_file_path )
            else:
                image_file_path = None
                resource.description = row[CSV_FORMAT['description']].decode('utf-8') 
                
            try:
                resource.id = api.add_resource(resource)
            except ORBAPIResourceExistsException, e:
                if DEBUG:
                    print e.message + ", id no:" + str(e.pk)
                resource.id = e.pk  
                api.update_resource(resource)
     
            # get the resource id
            resource_from_api = api.get_resource(resource)
            
            # remove all ResourceFiles
            api.delete_resource_files(resource_from_api['files'])
                
            # remove all ResourceURLs
            api.delete_resource_urls(resource_from_api['urls'])
            
            # remove all tags for resource
            api.delete_resource_tags(resource_from_api['tags'])
                
            if image_file_path:
                api.add_or_update_resource_image(resource.id, image_file_path)
            
                
            # add resource specific tags
            specific_tags = row[CSV_FORMAT['license']] + "," + row[CSV_FORMAT['resource-type']] + "," + row[CSV_FORMAT['organisation']] + "," + row[CSV_FORMAT['health-domain']] + "," + row[CSV_FORMAT['audience']] + "," + row[CSV_FORMAT['geography']]
            tag_list = [x.strip() for x in specific_tags.split(',')]
            for tag in tag_list:
                api.add_resource_tag(resource.id, tag.strip())
                
            for lang in LANGUAGES:
                if row[CSV_FORMAT[lang]].strip() != "":
                    if DEBUG:
                        print "adding url: " + row[CSV_FORMAT[lang]]
                    resource_url = orb_resource_url()
                    resource_url.title = "View/Download ("+ lang +")"
                    resource_url.url = row[CSV_FORMAT[lang]]
                
                    api.add_resource_url(resource.id, resource_url)
                    api.add_resource_tag(resource.id, lang.strip())
                
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("orb_url", help="ORB url")
    parser.add_argument("orb_username", help="ORB User Name")
    parser.add_argument("orb_key", help="ORB API Key")
    args = parser.parse_args()
    run(args.orb_url, args.orb_username, args.orb_key)