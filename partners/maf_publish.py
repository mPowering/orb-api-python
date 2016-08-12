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
   
INFILE = os.path.join(BASE_DIR, 'maf_data', 'MAF-ORB-data.csv')

CSV_FORMAT = {
              'title': 0,
              'description': 1,
              'health-domain': 2,
              'audience': 3,
              'language': 4,
              'geography': 5,
              'study_time': 6,
              'preview': 7,
              'download_hq': 8,
              'download_mq': 9,
              'download_lq': 10,
              'French':11,
              'Swahili':12,
              'Somali':13,
              'Amharic':14,
              'Portugese':15,
              'Dari':16,
              'Bemba':17,
              'Luganda':18,
              'Yoruba':19,
              'Hausa': 20,
              'Saint Lucian Creole': 21,
              'Khmer':22,
              'Burmese':23,
              'Vietnamese':24,
              'Indonesian':25,
              'Kinyarwanda':26,
              
              }

MPOWERING_DEFAULT_TAGS = ["Medical Aid Films",
                          "Video",  
                          "Laptop", 
                          "Smartphone", 
                          "Tablet", 
                          "Creative Commons 3.0 (CC-BY-NC-ND)",]

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
            
            # get the video info from Vimeo
            req = urllib2.Request("https://vimeo.com/api/oembed.json?maxwidth=500&url=" + row[CSV_FORMAT['preview']], 
                                  headers={ 'User-Agent': 'Mozilla/5.0',
                                           })
            response = urllib2.urlopen(req)
            if response.code == HTML_OK:
                vimeo_data = json.loads(response.read())
            else:
                if DEBUG:
                    print "Error connecting to Vimeo server"
                continue 
            
            resource.description = row[CSV_FORMAT['description']].decode('utf-8') + '<div style="text-align:center;">' + vimeo_data['html'].decode('utf-8') + '</div>'
            
            if row[CSV_FORMAT['study_time']] != '':
                resource.study_time_number = row[CSV_FORMAT['study_time']]
                resource.study_time_unit = 'mins'
                
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
                
            # get resource image from vimeo
            image_file_path = os.path.join('/tmp', str(vimeo_data['video_id']) + '.jpg')
            urllib.urlretrieve (vimeo_data['thumbnail_url'], image_file_path )
            
            api.add_or_update_resource_image(resource.id, image_file_path)
            
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
                if DEBUG:
                    print "adding url: " + row[CSV_FORMAT['preview']]
                resource_url = orb_resource_url()
                resource_url.title = "View/Download on Vimeo (" + row[CSV_FORMAT['language']] + ")"
                resource_url.url = row[CSV_FORMAT['preview']]
            
                api.add_resource_url(resource.id,resource_url)
                
            other_langs_list = ['French', 
                                'Swahili', 
                                'Somali', 
                                'Amharic', 
                                'Portugese', 
                                'Dari', 
                                'Bemba', 
                                'Luganda', 
                                'Yoruba',
                                'Hausa',
                                'Saint Lucian Creole',
                                'Khmer',
                                'Burmese',
                                'Vietnamese',
                                'Indonesian',
                                'Kinyarwanda',]
            for ol in other_langs_list:
                if row[CSV_FORMAT[ol]].strip() != "":
                    if DEBUG:
                        print "adding url: " + row[CSV_FORMAT[ol]]
                    resource_url = orb_resource_url()
                    resource_url.title = "View/Download on Vimeo ("+ ol +")"
                    resource_url.url = row[CSV_FORMAT[ol]]
                
                    api.add_resource_url(resource.id, resource_url)
                    api.add_resource_tag(resource.id, ol.strip())
                        
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("orb_url", help="ORB url")
    parser.add_argument("orb_username", help="ORB User Name")
    parser.add_argument("orb_key", help="ORB API Key")
    args = parser.parse_args()
    run(args.orb_url, args.orb_username, args.orb_key)
