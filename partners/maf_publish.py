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
    
from api import orb_api, orb_resource, orb_resource_file, orb_resource_url
from error_codes import * 
   
INFILE = os.path.join(BASE_DIR, 'maf_data', 'MAF-ORB-data.csv')

CSV_FORMAT = {
              'title': 0,
              'description': 1,
              'health-domain': 2,
              'audience': 3,
              'language': 4,
              'geography': 5,
              'preview': 6,
              'download_hq': 7,
              'download_mq': 8,
              'download_lq': 9
              
              }

MPOWERING_DEFAULT_TAGS = ["Medical Aid Films",
                          "Video",  
                          "Laptop", 
                          "Smartphone", 
                          "Tablet", 
                          "Creative Commons 3.0 (CC-BY-NC-ND)"]

def run(orb_username, orb_key): 
    api = orb_api()
    api.base_url = 'http://localhost:8000'
    api.user_name = orb_username
    api.api_key = orb_key    
    
    with open(INFILE, 'rb') as csvfile:
        file_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for counter, row in enumerate(file_reader):
            # skip first row as has the headings
            if counter == 0:
                continue
            
            # skip it no title
            if row[CSV_FORMAT['title']].strip() == "":
                continue
            
            resource = orb_resource()
            resource.title =  row[CSV_FORMAT['title']]
            
            # get the video info from Vimeo
            req = urllib2.Request("https://vimeo.com/api/oembed.json?maxwidth=500&url=" + row[CSV_FORMAT['preview']], 
                                  headers={ 'User-Agent': 'Mozilla/5.0',
                                           })
            response = urllib2.urlopen(req)
            if response.code == HTML_OK:
                vimeo_data = json.loads(response.read())
            else:
                print "Error connecting to Vimeo server"
                continue 
            
            resource.description = row[CSV_FORMAT['description']].decode('utf-8') + '<div style="text-align:center;">' + vimeo_data['html'].decode('utf-8') + '</div>'
            
            resource.id = api.add_resource(resource)
            
            if resource.id:
                
                # get resource image from vimeo
                image_file_path = os.path.join('/tmp', str(vimeo_data['video_id']) + '.jpg')
                urllib.urlretrieve (vimeo_data['thumbnail_url'], image_file_path )
                
                api.add_resource_image(resource.id, image_file_path)
                
                
                
                # add all the default tags
                for tag in MPOWERING_DEFAULT_TAGS:
                    api.add_resource_tag(resource.id, tag.strip())
                    
                # add resource specific tags
                specific_tags = row[CSV_FORMAT['health-domain']] + "," + row[CSV_FORMAT['audience']] + "," + row[CSV_FORMAT['language']] + "," + row[CSV_FORMAT['geography']]
                tag_list = [x.strip() for x in specific_tags.split(',')]
                for tag in tag_list:
                    api.add_resource_tag(resource.id, tag.strip())
                    
                    
                # add the urls/downloads
                if row[CSV_FORMAT['preview']].strip() != "":
                    print "adding url: " + row[CSV_FORMAT['preview']]
                    resource_url = orb_resource_url()
                    resource_url.title = "View/Download on Vimeo"
                    resource_url.url = row[CSV_FORMAT['preview']]
                    # attempt to get file size
                    '''
                    try:
                        response = urllib2.urlopen(row[CSV_FORMAT['preview']])
                        resource_url.file_size = response.headers['Content-Length']
                    except:
                        resource_url.file_size = 0
                    '''
                        
                    api.add_resource_url(resource.id,resource_url)
                    
                '''
                if row[CSV_FORMAT['download_hq']].strip() != "":
                    print "adding url: " + row[CSV_FORMAT['download_hq']]
                    resource_url = orb_resource_url()
                    resource_url.title = "High Definition - for Projection"
                    resource_url.url = row[CSV_FORMAT['download_hq']]
                    # attempt to get file size
                    try:
                        response = urllib2.urlopen(row[CSV_FORMAT['download_hq']])
                        resource_url.file_size = response.headers['Content-Length']
                    except:
                        resource_url.file_size = 0
                        
                    api.add_resource_url(resource.id,resource_url)
                
                if row[CSV_FORMAT['download_mq']].strip() != "":
                    print "adding url: " + row[CSV_FORMAT['download_mq']]
                    resource_url = orb_resource_url()
                    resource_url.title = "Medium Resolution - for Laptop/Desktop"
                    resource_url.url = row[CSV_FORMAT['download_mq']]
                    # attempt to get file size
                    try:
                        response = urllib2.urlopen(row[CSV_FORMAT['download_mq']])
                        resource_url.file_size = response.headers['Content-Length']
                    except:
                        resource_url.file_size = 0
                        
                    api.add_resource_url(resource.id,resource_url)
                
                if row[CSV_FORMAT['download_lq']].strip() != "":
                    print "adding url: " + row[CSV_FORMAT['download_lq']]
                    resource_url = orb_resource_url()
                    resource_url.title = "Low Resolution - for Mobile Devices"
                    resource_url.url = row[CSV_FORMAT['download_lq']]
                    # attempt to get file size
                    try:
                        response = urllib2.urlopen(row[CSV_FORMAT['download_lq']])
                        resource_url.file_size = response.headers['Content-Length']
                    except:
                        resource_url.file_size = 0
                        
                    api.add_resource_url(resource.id,resource_url)
                '''
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("orb_username", help="ORB User Name")
    parser.add_argument("orb_key", help="ORB API Key")
    args = parser.parse_args()
    run(args.orb_username, args.orb_key)
