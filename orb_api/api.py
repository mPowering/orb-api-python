#!/usr/bin/python
import json
import urllib2
import urllib

from poster.encode import multipart_encode
from poster.streaminghttp import register_openers


class orb_api():
    base_url = ''
    user_name = ''
    api_key = ''
    
    def search(self, query):
        req = urllib2.Request(self.base_url + '/api/v1/resource/search/?q='+query)
        req.add_header('Authorization', 'ApiKey '+self.user_name + ":" + self.api_key)
        resp = urllib2.urlopen(req)
        data = resp.read()
        dataJSON = json.loads(data)
        return dataJSON
    
    def add_resource(self,resource):
        data = json.dumps({'title': resource.title, 'description': resource.description })
        
        # make a string with the request type in it:
        method = "POST"
        # create a handler. you can specify different handlers here (file uploads etc)
        # but we go for the default
        handler = urllib2.HTTPHandler()
        # create an openerdirector instance
        opener = urllib2.build_opener(handler)
        # build a request
        request = urllib2.Request(self.base_url + '/api/v1/resource/', data=data )
        # add any other information you want
        request.add_header("Content-Type",'application/json')
        request.add_header('Authorization', 'ApiKey '+self.user_name + ":" + self.api_key)
        # overload the get method function with a small anonymous function...
        request.get_method = lambda: method
        # try it; don't forget to catch the result
        try:
            connection = opener.open(request)
        except urllib2.HTTPError,e:
            connection = e
            
        if connection.code == 401:
            # unauthorised
            pass
        elif connection.code == 400:
            # already exists or other error
            pass
        elif connection.code == 500:
            # already exists or other error
            print connection.read()
        elif connection.code == 201:
            # success
            resp = connection.read()
            data_json = json.loads(resp)
            return data_json['id']
            
        return
    
    def get_resource(self, resource):
        return
    
    def add_resource_image(self, resource_id, image_file):
        register_openers()
        
        datagen, headers = multipart_encode({'resource_id': resource_id, 'image_file': open(image_file)})
        handler = urllib2.HTTPHandler()
        request = urllib2.Request(self.base_url + '/api/upload/image/', datagen, headers )
        request.add_header('Authorization', 'ApiKey '+self.user_name + ":" + self.api_key)
        
        resp = urllib2.urlopen(request)
        if resp.code == 401:
            # unauthorised
            print resp.code
            print resp.read()
        elif resp.code == 400:
            # already exists or other error
            print resp.code
            print resp.read()
        elif resp.code == 500:
            # already exists or other error
            print resp.code
            print resp.read()
        elif resp.code == 201:
            print "Uploaded Image: " + image_file
        
        return
    
    def add_resource_file(self,resource_id, resource_file):
        register_openers()
        
        datagen, headers = multipart_encode({'resource_id': resource_id,
                                             'title': resource_file.title,
                                             'description': resource_file.description, 
                                             'resource_file': open(resource_file.file)})
        handler = urllib2.HTTPHandler()
        request = urllib2.Request(self.base_url + '/api/upload/file/', datagen, headers )
        request.add_header('Authorization', 'ApiKey '+self.user_name + ":" + self.api_key)
        
        resp = urllib2.urlopen(request)
        
        if resp.code == 401:
            # unauthorised
            print resp.code
            print resp.read()
        elif resp.code == 400:
            # already exists or other error
            print resp.code
            print resp.read()
        elif resp.code == 500:
            # already exists or other error
            print resp.code
            print resp.read()
        elif resp.code == 201:
            print "Uploaded: " + resource_file.title
        
        return
    
    def add_resource_tag(self,resource_id, tag_name):
        # find the tag id 
        tag_name_obj = { "name": tag_name }
        
        req = urllib2.Request(self.base_url + '/api/v1/tag/?' + urllib.urlencode(tag_name_obj))
        req.add_header('Authorization', 'ApiKey '+self.user_name + ":" + self.api_key)
        req.add_header('Accept', 'application/json')

        connection = urllib2.urlopen(req)

        resp = connection.read()
        
        if connection.code == 200:
            data_json = json.loads(resp)
            if data_json['meta']['total_count'] == 1:
                tag = data_json['objects'][0]
            else:
                tag = self.__create_tag(tag_name)
                
            # add tagresource
            self.__create_resourcetag(resource_id,tag['id'])
        else: 
            print connection.code
        
        return
    
    def __create_tag(self,tag_name):
        
        data = json.dumps({'name': tag_name })
        
        method = "POST"
        # create a handler. you can specify different handlers here (file uploads etc)
        # but we go for the default
        handler = urllib2.HTTPHandler()
        # create an openerdirector instance
        opener = urllib2.build_opener(handler)
        # build a request
        request = urllib2.Request(self.base_url + '/api/v1/tag/', data=data )
        # add any other information you want
        request.add_header("Content-Type",'application/json')
        request.add_header('Authorization', 'ApiKey '+self.user_name + ":" + self.api_key)
        
        request.get_method = lambda: method
        # try it; don't forget to catch the result
        try:
            connection = opener.open(request)
        except urllib2.HTTPError,e:
            connection = e
         
        if connection.code == 401:
            # unauthorised
            pass
        elif connection.code == 400:
            # already exists or other error
            pass
        elif connection.code == 500:
            # already exists or other error
            print connection.read()
        elif connection.code == 201:
            # success
            resp = connection.read()
            data_json = json.loads(resp)
            return data_json
           
        return
    
    def __create_resourcetag(self, resource_id, tag_id):
        
        data  = json.dumps({'resource_id': resource_id, 'tag_id': tag_id })       
        method = "POST"
        # create a handler. you can specify different handlers here (file uploads etc)
        # but we go for the default
        handler = urllib2.HTTPHandler()
        # create an openerdirector instance
        opener = urllib2.build_opener(handler)
        # build a request
        request = urllib2.Request(self.base_url + '/api/v1/resourcetag/', data=data )
        # add any other information you want
        request.add_header("Content-Type",'application/json')
        request.add_header('Authorization', 'ApiKey '+self.user_name + ":" + self.api_key)
        
        request.get_method = lambda: method
        # try it; don't forget to catch the result
        try:
            connection = opener.open(request)
        except urllib2.HTTPError,e:
            connection = e
         
        if connection.code == 401:
            # unauthorised
            pass
        elif connection.code == 400:
            # already exists or other error
            pass
        elif connection.code == 500:
            # already exists or other error
            print connection.read()
        elif connection.code == 201:
            # success
            resp = connection.read()
            data_json = json.loads(resp)
            return data_json
           
        return
    
class orb_resource():
    id = None
    title = ''
    description = ''
    
class orb_resource_file():
    file = ''
    title = ''
    description = ''
    
class orb_resource_url():
    url = ''
    title = ''
    description = ''
    
       
    
    