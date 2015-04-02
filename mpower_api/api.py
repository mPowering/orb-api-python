import urllib2
import json

class mpower_api():
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
    
    
    
    def send(self):
        return
    
    