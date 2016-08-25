#!/usr/bin/python
import json
import re
import urllib2
import urllib
import time

from error_codes import * 
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import code

API_PATH = '/api/v1/'

class orb_api():
    base_url = ''
    user_name = ''
    api_key = ''
    sleep = 0
    verbose_output = False
    
    def search(self, query):
        req = urllib2.Request(self.base_url + API_PATH + 'resource/search/?q='+query)
        req.add_header('Authorization', 'ApiKey '+self.user_name + ":" + self.api_key)
        resp = urllib2.urlopen(req)
        data = resp.read()
        dataJSON = json.loads(data)
        return dataJSON
    
    def add_resource(self,resource):
        # add in script pause to save overloading server and API limits
        time.sleep(self.sleep)
        
        data = json.dumps({'title': resource.title, 
                           'description': resource.description,
                           'study_time_number': resource.study_time_number,
                           'study_time_unit': resource.study_time_unit,
                           'attribution': resource.attribution })
        
        method = "POST"
        handler = urllib2.HTTPHandler()
        opener = urllib2.build_opener(handler)
        request = urllib2.Request(self.base_url + API_PATH + 'resource/', data=data )
        request.add_header("Content-Type",'application/json')
        request.add_header('Authorization', 'ApiKey '+self.user_name + ":" + self.api_key)
        request.get_method = lambda: method

        try:
            connection = opener.open(request)
        except urllib2.HTTPError,e:
            connection = e
           
        resp = connection.read()
         
        if self.verbose_output:
            print "Submitting: " + resource.title
            
        if connection.code == HTML_UNAUTHORIZED:
            raise ORBAPIException("Unauthorized", HTML_UNAUTHORIZED)
        elif connection.code == HTML_BADREQUEST:
            json_resp = json.loads(resp)
            error = json.loads(json_resp["error"])
            if error["code"] == ERROR_CODE_RESOURCE_EXISTS:
                raise ORBAPIResourceExistsException(error["message"], error["code"], error["pk"])
            else:
                raise ORBAPIException(error["message"],error["code"])
        elif connection.code == HTML_SERVERERROR:
            if self.verbose_output:
                print resp
            raise ORBAPIException("Connection or Server Error", HTML_SERVERERROR)
        elif connection.code == HTML_CREATED:
            # success
            data_json = json.loads(resp)
            if self.verbose_output:
                print "added: " + str(data_json['id']) + " : " + resource.title
            return data_json['id']
        elif connection.code == HTML_TOO_MANY_REQUESTS:
            raise ORBAPIException("Too many API requests - you have been throttled", HTML_TOO_MANY_REQUESTS)
            exit()
            
        return
    
    def update_resource(self,resource):
        # add in script pause to save overloading server and API limits
        time.sleep(self.sleep)
        
        data = json.dumps({'title': resource.title, 
                           'description': resource.description,
                           'study_time_number': resource.study_time_number,
                           'study_time_unit': resource.study_time_unit,
                           'attribution': resource.attribution })
        
        method = "PUT"
        handler = urllib2.HTTPHandler()
        opener = urllib2.build_opener(handler)
        request = urllib2.Request(self.base_url + API_PATH + 'resource/' + str(resource.id) + '/', data=data )
        request.add_header("Content-Type",'application/json')
        request.add_header('Authorization', 'ApiKey '+self.user_name + ":" + self.api_key)
        request.get_method = lambda: method

        try:
            connection = opener.open(request)
        except urllib2.HTTPError,e:
            connection = e
           
        resp = connection.read()
         
        if self.verbose_output:
            print "Updating: " + resource.title
            
        if connection.code == HTML_UNAUTHORIZED:
            raise ORBAPIException("Unauthorized", HTML_UNAUTHORIZED)
        elif connection.code == HTML_BADREQUEST:
            json_resp = json.loads(resp)
            error = json.loads(json_resp["error"])
            if error["code"] == ERROR_CODE_RESOURCE_EXISTS:
                raise ORBAPIResourceExistsException(error["message"], error["code"], error["pk"])
            else:
                raise ORBAPIException(error["message"],error["code"])
        elif connection.code == HTML_SERVERERROR:
            raise ORBAPIException("Connection or Server Error", HTML_SERVERERROR)
        elif connection.code == HTML_CREATED:
            # success
            data_json = json.loads(resp)
            if self.verbose_output:
                print "added: " + str(data_json['id']) + " : " + resource.title
            return data_json['id']
        elif connection.code == HTML_TOO_MANY_REQUESTS:
            raise ORBAPIException("Too many API requests - you have been throttled", HTML_TOO_MANY_REQUESTS)
            exit()
            
        return
    
    def get_resource(self, resource):
        
        req = urllib2.Request(self.base_url + API_PATH + 'resource/' + str(resource.id))
        req.add_header('Authorization', 'ApiKey '+self.user_name + ":" + self.api_key)
        req.add_header('Accept', 'application/json')

        connection = urllib2.urlopen(req)

        resp = connection.read()
        
        if connection.code == HTML_OK:
            data_json = json.loads(resp)
            return data_json
        elif resp.code == HTML_UNAUTHORIZED:
            raise ORBAPIException("Unauthorized", HTML_UNAUTHORIZED)
        else:
            raise ORBAPIException("Connection or Server Error", HTML_SERVERERROR)
        return
    
    def add_or_update_resource_image(self, resource_id, image_file):
        # add in script pause to save overloading server and API limits
        time.sleep(self.sleep)

        register_openers()
        datagen, headers = multipart_encode({'resource_id': resource_id, 
                                             'image_file': open(image_file)})
        handler = urllib2.HTTPHandler()
        request = urllib2.Request(self.base_url + '/api/upload/image/', datagen, headers )
        request.add_header('Authorization', 'ApiKey '+self.user_name + ":" + self.api_key)
        
        resp = urllib2.urlopen(request)
        if resp.code == HTML_UNAUTHORIZED:
            raise ORBAPIException("Unauthorized", HTML_UNAUTHORIZED)
        elif resp.code == HTML_BADREQUEST:
            json_resp = json.loads(resp.read())
            error = json.loads(json_resp["error"])
            raise ORBAPIException(error["message"],error["code"])
        elif resp.code == HTML_SERVERERROR:
           raise ORBAPIException("Connection or Server Error", HTML_SERVERERROR)
        elif resp.code == HTML_CREATED:
            if self.verbose_output:
                print "Uploaded Image: " + image_file
        
        return
    
    def add_resource_file(self,resource_id, resource_file):
        # add in script pause to save overloading server and API limits
        time.sleep(self.sleep)
        
        register_openers()
        
        datagen, headers = multipart_encode({'resource_id': resource_id,
                                             'title': resource_file.title,
                                             'description': resource_file.description, 
                                             'order_by': resource_file.order_by, 
                                             'resource_file': open(resource_file.file)})
        handler = urllib2.HTTPHandler()
        request = urllib2.Request(self.base_url + '/api/upload/file/', datagen, headers )
        request.add_header('Authorization', 'ApiKey '+self.user_name + ":" + self.api_key)
        
        resp = urllib2.urlopen(request)
        
        if resp.code == HTML_UNAUTHORIZED:
            raise ORBAPIException("Unauthorized", HTML_UNAUTHORIZED)
        elif resp.code == HTML_BADREQUEST:
            json_resp = json.loads(resp.read())
            error = json.loads(json_resp["error"])
            raise ORBAPIException(error["message"],error["code"])
        elif resp.code == HTML_SERVERERROR:
            raise ORBAPIException("Connection or Server Error", HTML_SERVERERROR)
        elif resp.code == HTML_CREATED:
            if self.verbose_output:
                print "Uploaded: " + resource_file.title
        
        return
    
    def delete_resource_files(self,resource_files):
        # add in script pause to save overloading server and API limits
        time.sleep(self.sleep)
        for f in resource_files:
            method = "DELETE"
            handler = urllib2.HTTPHandler()
            opener = urllib2.build_opener(handler)
            request = urllib2.Request(self.base_url + f['resource_uri'])
            request.add_header("Content-Type",'application/json')
            request.add_header('Authorization', 'ApiKey '+self.user_name + ":" + self.api_key)
            request.get_method = lambda: method
            try:
                connection = opener.open(request)
            except urllib2.HTTPError,e:
                connection = e
               
            resp = connection.read()
    
            if connection.code == HTML_UNAUTHORIZED:
                raise ORBAPIException("Unauthorized", HTML_UNAUTHORIZED)
            elif connection.code == HTML_BADREQUEST:
                json_resp = json.loads(resp)
                error = json.loads(json_resp["error"])
                if error["code"] == ERROR_CODE_RESOURCE_EXISTS:
                    if self.verbose_output:
                        print error["message"]
                else:
                    raise ORBAPIException(error["message"],error["code"])
            elif connection.code == HTML_SERVERERROR:
                raise ORBAPIException("Connection or Server Error", HTML_SERVERERROR)
            elif connection.code == HTML_NO_CONTENT:
                pass # success
        return
    
    def add_resource_url(self,resource_id, resource_url):
        # add in script pause to save overloading server and API limits
        time.sleep(self.sleep)
        
        data = json.dumps({'title': resource_url.title, 
                           'description': resource_url.description,
                           'url': resource_url.url,
                           'order_by': resource_url.order_by,
                           'file_size': resource_url.file_size,
                           'resource_id': resource_id,})
        
        method = "POST"
        handler = urllib2.HTTPHandler()
        opener = urllib2.build_opener(handler)
        request = urllib2.Request(self.base_url + API_PATH + 'resourceurl/', data=data )
        request.add_header("Content-Type",'application/json')
        request.add_header('Authorization', 'ApiKey '+self.user_name + ":" + self.api_key)
        request.get_method = lambda: method

        try:
            connection = opener.open(request)
        except urllib2.HTTPError,e:
            connection = e
           
        resp = connection.read()
         
        if self.verbose_output:
            print "Adding: " + resource_url.title
        if connection.code == HTML_UNAUTHORIZED:
            raise ORBAPIException("Unauthorized", HTML_UNAUTHORIZED)
        elif connection.code == HTML_BADREQUEST:
            json_resp = json.loads(resp)
            error = json.loads(json_resp["error"])
            if error["code"] == ERROR_CODE_RESOURCE_EXISTS:
                if self.verbose_output:
                    print error["message"]
                    print "Updating..."
            else:
                raise ORBAPIException(error["message"],error["code"])
        elif connection.code == HTML_SERVERERROR:
            raise ORBAPIException("Connection or Server Error", HTML_SERVERERROR)
        elif connection.code == HTML_CREATED:
            # success
            data_json = json.loads(resp)
            if self.verbose_output:
                print "added: " + str(data_json['id']) + " : " + resource_url.title
            return data_json['id']
            
        return
    
    def delete_resource_urls(self,resource_urls):
        # add in script pause to save overloading server and API limits
        time.sleep(self.sleep)
        for f in resource_urls:
            method = "DELETE"
            handler = urllib2.HTTPHandler()
            opener = urllib2.build_opener(handler)
            request = urllib2.Request(self.base_url + f['resource_uri'])
            request.add_header("Content-Type",'application/json')
            request.add_header('Authorization', 'ApiKey '+self.user_name + ":" + self.api_key)
            request.get_method = lambda: method
            try:
                connection = opener.open(request)
            except urllib2.HTTPError,e:
                connection = e
               
            resp = connection.read()
    
            if connection.code == HTML_UNAUTHORIZED:
                raise ORBAPIException("Unauthorized", HTML_UNAUTHORIZED)
            elif connection.code == HTML_BADREQUEST:
                json_resp = json.loads(resp)
                error = json.loads(json_resp["error"])
                if error["code"] == ERROR_CODE_RESOURCE_EXISTS:
                    if self.verbose_output:
                        print error["message"]
                else:
                    raise ORBAPIException(error["message"],error["code"])
            elif connection.code == HTML_SERVERERROR:
                raise ORBAPIException("Connection or Server Error", HTML_SERVERERROR)
            elif connection.code == HTML_NO_CONTENT:
                pass # success
        return
    
    def add_resource_tag(self,resource_id, tag_name):
        # add in script pause to save overloading server and API limits
        time.sleep(self.sleep)
        
        if self.verbose_output:
            print "adding tag: " + tag_name.strip()
        
        regex = re.compile('[,\.!?"\']')
        if regex.sub('', tag_name.strip()) == '':
            return
        
        # find the tag id 
        tag_name_obj = { "name": tag_name }
        
        url = self.base_url + API_PATH + 'tag/?' + urllib.urlencode(tag_name_obj)
        print url
        req = urllib2.Request(url)
        req.add_header('Authorization', 'ApiKey '+self.user_name + ":" + self.api_key)
        req.add_header('Accept', 'application/json')

        connection = urllib2.urlopen(req)

        resp = connection.read()
        
        if connection.code == HTML_OK:
            data_json = json.loads(resp)
            if data_json['meta']['total_count'] == 1:
                tag = data_json['objects'][0]
            else:
                tag = self.__create_tag(tag_name)
                
            # add tagresource
            if tag is not None:
                self.__create_resourcetag(resource_id,tag['id'])
        else:
            if self.verbose_output: 
                print connection.code
        
        if self.verbose_output:
            print "added tag: " + tag_name.strip()
        return
    
    def delete_resource_tags(self, resource_tags):
         # add in script pause to save overloading server and API limits
        time.sleep(self.sleep)
        for rt in resource_tags:
            method = "DELETE"
            handler = urllib2.HTTPHandler()
            opener = urllib2.build_opener(handler)
            request = urllib2.Request(self.base_url + rt['resource_uri'])
            request.add_header("Content-Type",'application/json')
            request.add_header('Authorization', 'ApiKey '+self.user_name + ":" + self.api_key)
            request.get_method = lambda: method
            try:
                connection = opener.open(request)
            except urllib2.HTTPError,e:
                connection = e
               
            resp = connection.read()
    
            if connection.code == HTML_UNAUTHORIZED:
                raise ORBAPIException("Unauthorized", HTML_UNAUTHORIZED)
            elif connection.code == HTML_BADREQUEST:
                json_resp = json.loads(resp)
                error = json.loads(json_resp["error"])
                raise ORBAPIException(error["message"],error["code"])
            elif connection.code == HTML_SERVERERROR:
                raise ORBAPIException("Connection or Server Error", HTML_SERVERERROR)
            elif connection.code == HTML_NO_CONTENT:
                pass # success
        return
        
    
    def __create_tag(self,tag_name):
        
        data = json.dumps({'name': tag_name })
        
        method = "POST"
        handler = urllib2.HTTPHandler()
        opener = urllib2.build_opener(handler)
        request = urllib2.Request(self.base_url + API_PATH + 'tag/', data=data )
        request.add_header("Content-Type",'application/json')
        request.add_header('Authorization', 'ApiKey '+self.user_name + ":" + self.api_key)
        request.get_method = lambda: method

        try:
            connection = opener.open(request)
        except urllib2.HTTPError,e:
            connection = e
        
        resp = connection.read()
        if connection.code == HTML_UNAUTHORIZED:
            raise ORBAPIException("Unauthorized", HTML_UNAUTHORIZED)
        elif connection.code == HTML_BADREQUEST:
            json_resp = json.loads(resp)
            error = json.loads(json_resp["error"])
            if error["code"] == ERROR_CODE_TAG_EMPTY:
                return
            raise ORBAPIException(error["message"],error["code"])
        elif connection.code == HTML_SERVERERROR:
            if self.verbose_output:
                print resp
            raise ORBAPIException("Connection or Server Error", HTML_SERVERERROR)
        elif connection.code == HTML_CREATED:
            # success
            data_json = json.loads(resp)
            return data_json
           
        return
    
    def __create_resourcetag(self, resource_id, tag_id):
        
        data  = json.dumps({'resource_id': resource_id, 'tag_id': tag_id })       
        method = "POST"
        handler = urllib2.HTTPHandler()
        opener = urllib2.build_opener(handler)
        request = urllib2.Request(self.base_url + API_PATH + 'resourcetag/', data=data )
        request.add_header("Content-Type",'application/json')
        request.add_header('Authorization', 'ApiKey '+self.user_name + ":" + self.api_key)
        request.get_method = lambda: method
        try:
            connection = opener.open(request)
        except urllib2.HTTPError,e:
            connection = e
         
        if connection.code == HTML_UNAUTHORIZED:
            raise ORBAPIException("Unauthorized", HTML_UNAUTHORIZED)
        elif connection.code == HTML_BADREQUEST:
            json_resp = json.loads(connection.read())
            error = json.loads(json_resp["error"])
            if error["code"] == ERROR_CODE_RESOURCETAG_EXISTS:
                if self.verbose_output:
                    print error["message"]
                return
            else:
                raise ORBAPIException(error["message"],error["code"])
                #pass
        elif connection.code == HTML_SERVERERROR:
            raise ORBAPIException("Connection or Server Error", HTML_SERVERERROR)
        elif connection.code == HTML_CREATED:
            # success
            resp = connection.read()
            data_json = json.loads(resp)
            return data_json
           
        return
    
class orb_resource():
    id = None
    title = None
    description = None
    study_time_number = 0
    study_time_unit = None
    attribution = None
    
class orb_resource_file():
    file = ''
    title = ''
    description = ''
    order_by = 0
    
class orb_resource_url():
    url = ''
    title = ''
    description = ''
    order_by = 0
    file_size = 0
    
        
class ORBAPIException(Exception):
    def __init__(self, message, error_code):
        
        # Call the base class constructor with the parameters it needs
        super(ORBAPIException, self).__init__(str(error_code) + ": " + message)
    
        # Now for your custom code...
        #self.errors = errors
        
class ORBAPIResourceExistsException(Exception):
    pk = None
    code = None
    message = None
    
    def __init__(self, message, error_code, pk):
        
        # Call the base class constructor with the parameters it needs
        super(ORBAPIResourceExistsException, self).__init__(str(error_code) + ": " + message)
    
        # Now for your custom code...
        self.pk = pk
        self.code = code
        self.message = message
       
    
    