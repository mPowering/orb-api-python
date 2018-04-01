#!/usr/bin/env python

# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json
import re
import time
import urllib
import urllib2
import warnings
from functools import wraps

import requests
from orb_api import error_codes
from orb_api.exceptions import OrbApiException, OrbApiResourceExists
from orb_api.models import OrbResource, OrbResourceFile, OrbResourceURL
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers

API_PATH = '/api/v1/'
GET = "GET"
POST = "POST"
DELETE = "DELETE"
PUT = "PUT"


def sleep_delay(func):
    @wraps(func)
    def inner(instance, *args, **kwargs):
        time.sleep(instance.sleep)
        return func(instance, *args, **kwargs)

    return inner


class OrbClient(object):
    """
    Client class for accessing the ORB API

    >>> client = OrbClient(host="http://localhost", username="bob", api_key="jdkjfkajkj")

    """

    def __init__(self, host, username, api_key, sleep=0, verbose=False):
        self.base_url = host
        self.user_name = username
        self.api_key = api_key
        self.sleep = sleep
        self.verbose_output = verbose

        self.session = requests.Session()
        self.session.auth = (self.user_name, self.api_key)
        self.session.headers.update({"Content-Type": "application/json"})

        self.param_defaults = {
            "format": "json",
            "username": self.user_name,
            "api_key": self.api_key,
        }

    @sleep_delay
    def request(self, method, path='', fullpath='', params=None, data=None):
        """
        General request handler for all HTTP calls.

        Args:
            method: HTTP method
            path: path relative to the API version info
            fullpath: optional full API path
            params: optional URL params (dict)
            data: optional body [POST] data (dict)

        Returns:
            Decoded JSON response

        """
        request_path = self.base_url + (fullpath if fullpath else API_PATH + path)
        params = params or {}
        data = data or {}

        # fullpath is presumed to include all parameters pre-loaded
        if not fullpath:
            params.update(self.param_defaults)

        response = self.session.request(method, request_path, params=params, data=data)
        response_json = response.json()

        if response.status_code >= 300:
            try:
                message = error_codes.messages[response.status_code]
            except KeyError:
                message = response_json["error"]
            raise OrbApiException(message, error_codes.HTML_UNAUTHORIZED)
        return response_json

    def get(self, path='', fullpath='', **kwargs):
        return self.request(GET, path, fullpath, **kwargs)

    def search(self, query):
        req = urllib2.Request(self.base_url + API_PATH + 'resource/search/?q=' + query)
        req.add_header('Authorization', 'ApiKey ' + self.user_name + ":" + self.api_key)
        resp = urllib2.urlopen(req)
        data = resp.read()
        return json.loads(data)

    def add_resource(self, resource):
        data = json.dumps({'title': resource.title,
                           'description': resource.description,
                           'study_time_number': resource.study_time_number,
                           'study_time_unit': resource.study_time_unit,
                           'attribution': resource.attribution})

        method = POST
        handler = urllib2.HTTPHandler()
        opener = urllib2.build_opener(handler)
        request = urllib2.Request(self.base_url + API_PATH + 'resource/', data=data)
        request.add_header("Content-Type", 'application/json')
        request.add_header('Authorization', 'ApiKey ' + self.user_name + ":" + self.api_key)
        request.get_method = lambda: method

        try:
            connection = opener.open(request)
        except urllib2.HTTPError as e:
            connection = e

        resp = connection.read()

        if self.verbose_output:
            print("Submitting: " + resource.title)

        if connection.code == error_codes.HTML_UNAUTHORIZED:
            raise OrbApiException("Unauthorized", error_codes.HTML_UNAUTHORIZED)
        elif connection.code == error_codes.HTML_BADREQUEST:
            json_resp = json.loads(resp)
            error = json.loads(json_resp["error"])
            if error["code"] == error_codes.ERROR_CODE_RESOURCE_EXISTS:
                raise OrbApiResourceExists(error["message"], error["code"], error["pk"])
            else:
                raise OrbApiException(error["message"], error["code"])
        elif connection.code == error_codes.HTML_SERVERERROR:
            if self.verbose_output:
                print(resp)
            raise OrbApiException("Connection or Server Error", error_codes.HTML_SERVERERROR)
        elif connection.code == error_codes.HTML_CREATED:
            # success
            data_json = json.loads(resp)
            if self.verbose_output:
                print("added: " + str(data_json['id']) + " : " + resource.title)
            return data_json['id']
        elif connection.code == error_codes.HTML_TOO_MANY_REQUESTS:
            raise OrbApiException("Too many API requests - you have been throttled", error_codes.HTML_TOO_MANY_REQUESTS)

        return

    @sleep_delay
    def update_resource(self, resource):
        data = json.dumps({'title': resource.title,
                           'description': resource.description,
                           'study_time_number': resource.study_time_number,
                           'study_time_unit': resource.study_time_unit,
                           'attribution': resource.attribution})

        method = PUT
        handler = urllib2.HTTPHandler()
        opener = urllib2.build_opener(handler)
        request = urllib2.Request(self.base_url + API_PATH + 'resource/' + str(resource.id) + '/', data=data)
        request.add_header("Content-Type", 'application/json')
        request.add_header('Authorization', 'ApiKey ' + self.user_name + ":" + self.api_key)
        request.get_method = lambda: method

        try:
            connection = opener.open(request)
        except urllib2.HTTPError as e:
            connection = e

        resp = connection.read()

        if self.verbose_output:
            print("Updating: " + resource.title)

        if connection.code == error_codes.HTML_UNAUTHORIZED:
            raise OrbApiException("Unauthorized", error_codes.HTML_UNAUTHORIZED)
        elif connection.code == error_codes.HTML_BADREQUEST:
            json_resp = json.loads(resp)
            error = json.loads(json_resp["error"])
            if error["code"] == error_codes.ERROR_CODE_RESOURCE_EXISTS:
                raise OrbApiResourceExists(error["message"], error["code"], error["pk"])
            else:
                raise OrbApiException(error["message"], error["code"])
        elif connection.code == error_codes.HTML_SERVERERROR:
            raise OrbApiException("Connection or Server Error", error_codes.HTML_SERVERERROR)
        elif connection.code == error_codes.HTML_CREATED:
            # success
            data_json = json.loads(resp)
            if self.verbose_output:
                print("added: " + str(data_json['id']) + " : " + resource.title)
            return data_json['id']
        elif connection.code == error_codes.HTML_TOO_MANY_REQUESTS:
            raise OrbApiException("Too many API requests - you have been throttled", error_codes.HTML_TOO_MANY_REQUESTS)

        return

    def _paginator(self, api_data):
        """
        Generator function that iterates through every object in the results,
        smoothing out the effects of API pagination.

        Args:
            api_data: the initial API data structure

        Yields:
            objects from the query and initial query until all are exhausted

        """
        for obj in api_data['objects']:
            yield obj

        while api_data['meta']['next']:
            api_data = self.get(fullpath=api_data['meta']['next'])
            try:
                for obj in api_data['objects']:
                    yield obj
            except KeyError:
                print(api_data.keys())
                print(api_data)
                raise

    def list_resources(self, limit=None, **kwargs):
        """

        Args:
            order_by: optional paramter to order the results
            limit: maximum number of results per page
            **kwargs: filtering arguments

        Returns:
            a tuple of the count of total items and a paginating generator

        """
        if limit:
            kwargs['limit'] = limit
        results = self.get("resource/", params=kwargs)
        return results['meta']['total_count'], self._paginator(results)

    def get_resource(self, resource):
        warnings.warn("Call get_resource_by_id directly", DeprecationWarning, stacklevel=2)
        return self.get_resource_by_id(resource.id)

    def get_resource_by_id(self, resource_id, **kwargs):
        return self.get("resource/{}/".format(resource_id, params=kwargs))

    @sleep_delay
    def add_or_update_resource_image(self, resource_id, image_file):
        register_openers()
        datagen, headers = multipart_encode({'resource_id': resource_id,
                                             'image_file': open(image_file)})

        request = urllib2.Request(self.base_url + '/api/upload/image/', datagen, headers)
        request.add_header('Authorization', 'ApiKey ' + self.user_name + ":" + self.api_key)

        resp = urllib2.urlopen(request)
        if resp.code == error_codes.HTML_UNAUTHORIZED:
            raise OrbApiException("Unauthorized", error_codes.HTML_UNAUTHORIZED)
        elif resp.code == error_codes.HTML_BADREQUEST:
            json_resp = json.loads(resp.read())
            error = json.loads(json_resp["error"])
            raise OrbApiException(error["message"], error["code"])
        elif resp.code == error_codes.HTML_SERVERERROR:
            raise OrbApiException("Connection or Server Error", error_codes.HTML_SERVERERROR)
        elif resp.code == error_codes.HTML_CREATED:
            if self.verbose_output:
                print("Uploaded Image: " + image_file)

    @sleep_delay
    def add_resource_file(self, resource_id, resource_file):
        register_openers()

        datagen, headers = multipart_encode({'resource_id': resource_id,
                                             'title': resource_file.title,
                                             'description': resource_file.description,
                                             'order_by': resource_file.order_by,
                                             'resource_file': open(resource_file.file)})
        request = urllib2.Request(self.base_url + '/api/upload/file/', datagen, headers)
        request.add_header('Authorization', 'ApiKey ' + self.user_name + ":" + self.api_key)

        resp = urllib2.urlopen(request)

        if resp.code == error_codes.HTML_UNAUTHORIZED:
            raise OrbApiException("Unauthorized", error_codes.HTML_UNAUTHORIZED)
        elif resp.code == error_codes.HTML_BADREQUEST:
            json_resp = json.loads(resp.read())
            error = json.loads(json_resp["error"])
            raise OrbApiException(error["message"], error["code"])
        elif resp.code == error_codes.HTML_SERVERERROR:
            raise OrbApiException("Connection or Server Error", error_codes.HTML_SERVERERROR)
        elif resp.code == error_codes.HTML_CREATED:
            if self.verbose_output:
                print("Uploaded: " + resource_file.title)

    @sleep_delay
    def delete_resource_files(self, resource_files):
        for f in resource_files:
            method = DELETE
            handler = urllib2.HTTPHandler()
            opener = urllib2.build_opener(handler)
            request = urllib2.Request(self.base_url + f['resource_uri'])
            request.add_header("Content-Type", 'application/json')
            request.add_header('Authorization', 'ApiKey ' + self.user_name + ":" + self.api_key)
            request.get_method = lambda: method
            try:
                connection = opener.open(request)
            except urllib2.HTTPError as e:
                connection = e

            resp = connection.read()

            if connection.code == error_codes.HTML_UNAUTHORIZED:
                raise OrbApiException("Unauthorized", error_codes.HTML_UNAUTHORIZED)
            elif connection.code == error_codes.HTML_BADREQUEST:
                json_resp = json.loads(resp)
                error = json.loads(json_resp["error"])
                if error["code"] == error_codes.ERROR_CODE_RESOURCE_EXISTS:
                    if self.verbose_output:
                        print(error["message"])
                else:
                    raise OrbApiException(error["message"], error["code"])
            elif connection.code == error_codes.HTML_SERVERERROR:
                raise OrbApiException("Connection or Server Error", error_codes.HTML_SERVERERROR)
            elif connection.code == error_codes.HTML_NO_CONTENT:
                pass  # success
        return

    @sleep_delay
    def add_resource_url(self, resource_id, resource_url):
        data = json.dumps({'title': resource_url.title,
                           'description': resource_url.description,
                           'url': resource_url.url,
                           'order_by': resource_url.order_by,
                           'file_size': resource_url.file_size,
                           'resource_id': resource_id, })

        method = POST
        handler = urllib2.HTTPHandler()
        opener = urllib2.build_opener(handler)
        request = urllib2.Request(self.base_url + API_PATH + 'resourceurl/', data=data)
        request.add_header("Content-Type", 'application/json')
        request.add_header('Authorization', 'ApiKey ' + self.user_name + ":" + self.api_key)
        request.get_method = lambda: method

        try:
            connection = opener.open(request)
        except urllib2.HTTPError as e:
            connection = e

        resp = connection.read()

        if self.verbose_output:
            print("Adding: " + resource_url.title)
        if connection.code == error_codes.HTML_UNAUTHORIZED:
            raise OrbApiException("Unauthorized", error_codes.HTML_UNAUTHORIZED)
        elif connection.code == error_codes.HTML_BADREQUEST:
            json_resp = json.loads(resp)
            error = json.loads(json_resp["error"])
            if error["code"] == error_codes.ERROR_CODE_RESOURCE_EXISTS:
                if self.verbose_output:
                    print(error["message"])
                    print("Updating...")
            else:
                raise OrbApiException(error["message"], error["code"])
        elif connection.code == error_codes.HTML_SERVERERROR:
            raise OrbApiException("Connection or Server Error", error_codes.HTML_SERVERERROR)
        elif connection.code == error_codes.HTML_CREATED:
            # success
            data_json = json.loads(resp)
            if self.verbose_output:
                print("added: " + str(data_json['id']) + " : " + resource_url.title)
            return data_json['id']

    @sleep_delay
    def delete_resource_urls(self, resource_urls):
        for f in resource_urls:
            method = DELETE
            handler = urllib2.HTTPHandler()
            opener = urllib2.build_opener(handler)
            request = urllib2.Request(self.base_url + f['resource_uri'])
            request.add_header("Content-Type", 'application/json')
            request.add_header('Authorization', 'ApiKey ' + self.user_name + ":" + self.api_key)
            request.get_method = lambda: method
            try:
                connection = opener.open(request)
            except urllib2.HTTPError as e:
                connection = e

            resp = connection.read()

            if connection.code == error_codes.HTML_UNAUTHORIZED:
                raise OrbApiException("Unauthorized", error_codes.HTML_UNAUTHORIZED)
            elif connection.code == error_codes.HTML_BADREQUEST:
                json_resp = json.loads(resp)
                error = json.loads(json_resp["error"])
                if error["code"] == error_codes.ERROR_CODE_RESOURCE_EXISTS:
                    if self.verbose_output:
                        print(error["message"])
                else:
                    raise OrbApiException(error["message"], error["code"])
            elif connection.code == error_codes.HTML_SERVERERROR:
                raise OrbApiException("Connection or Server Error", error_codes.HTML_SERVERERROR)
            elif connection.code == error_codes.HTML_NO_CONTENT:
                pass  # success

    @sleep_delay
    def add_resource_tag(self, resource_id, tag_name):
        if self.verbose_output:
            print("adding tag: " + tag_name.strip())

        regex = re.compile('[,\.!?"\']')
        if regex.sub('', tag_name.strip()) == '':
            return

        # find the tag id
        tag_name_obj = {"name": tag_name}

        url = self.base_url + API_PATH + 'tag/?' + urllib.urlencode(tag_name_obj)
        print(url)
        req = urllib2.Request(url)
        req.add_header('Authorization', 'ApiKey ' + self.user_name + ":" + self.api_key)
        req.add_header('Accept', 'application/json')

        connection = urllib2.urlopen(req)

        resp = connection.read()

        if connection.code == error_codes.HTML_OK:
            data_json = json.loads(resp)
            if data_json['meta']['total_count'] == 1:
                tag = data_json['objects'][0]
            else:
                tag = self.__create_tag(tag_name)

            # add tagresource
            if tag is not None:
                self.__create_resourcetag(resource_id, tag['id'])
        else:
            if self.verbose_output:
                print(connection.code)

        if self.verbose_output:
            print("added tag: " + tag_name.strip())

    @sleep_delay
    def delete_resource_tags(self, resource_tags):
        for rt in resource_tags:
            method = DELETE
            handler = urllib2.HTTPHandler()
            opener = urllib2.build_opener(handler)
            request = urllib2.Request(self.base_url + rt['resource_uri'])
            request.add_header("Content-Type", 'application/json')
            request.add_header('Authorization', 'ApiKey ' + self.user_name + ":" + self.api_key)
            request.get_method = lambda: method
            try:
                connection = opener.open(request)
            except urllib2.HTTPError as e:
                connection = e

            resp = connection.read()

            if connection.code == error_codes.HTML_UNAUTHORIZED:
                raise OrbApiException("Unauthorized", error_codes.HTML_UNAUTHORIZED)
            elif connection.code == error_codes.HTML_BADREQUEST:
                json_resp = json.loads(resp)
                error = json.loads(json_resp["error"])
                raise OrbApiException(error["message"], error["code"])
            elif connection.code == error_codes.HTML_SERVERERROR:
                raise OrbApiException("Connection or Server Error", error_codes.HTML_SERVERERROR)
            elif connection.code == error_codes.HTML_NO_CONTENT:
                pass  # success
        return

    def __create_tag(self, tag_name):

        data = json.dumps({'name': tag_name})

        method = POST
        handler = urllib2.HTTPHandler()
        opener = urllib2.build_opener(handler)
        request = urllib2.Request(self.base_url + API_PATH + 'tag/', data=data)
        request.add_header("Content-Type", 'application/json')
        request.add_header('Authorization', 'ApiKey ' + self.user_name + ":" + self.api_key)
        request.get_method = lambda: method

        try:
            connection = opener.open(request)
        except urllib2.HTTPError as e:
            connection = e

        resp = connection.read()
        if connection.code == error_codes.HTML_UNAUTHORIZED:
            raise OrbApiException("Unauthorized", error_codes.HTML_UNAUTHORIZED)
        elif connection.code == error_codes.HTML_BADREQUEST:
            json_resp = json.loads(resp)
            error = json.loads(json_resp["error"])
            if error["code"] == error_codes.ERROR_CODE_TAG_EMPTY:
                return
            raise OrbApiException(error["message"], error["code"])
        elif connection.code == error_codes.HTML_SERVERERROR:
            if self.verbose_output:
                print(resp)
            raise OrbApiException("Connection or Server Error", error_codes.HTML_SERVERERROR)
        elif connection.code == error_codes.HTML_CREATED:
            # success
            data_json = json.loads(resp)
            return data_json

        return

    def __create_resourcetag(self, resource_id, tag_id):

        data = json.dumps({'resource_id': resource_id, 'tag_id': tag_id})
        method = POST
        handler = urllib2.HTTPHandler()
        opener = urllib2.build_opener(handler)
        request = urllib2.Request(self.base_url + API_PATH + 'resourcetag/', data=data)
        request.add_header("Content-Type", 'application/json')
        request.add_header('Authorization', 'ApiKey ' + self.user_name + ":" + self.api_key)
        request.get_method = lambda: method
        try:
            connection = opener.open(request)
        except urllib2.HTTPError as e:
            connection = e

        if connection.code == error_codes.HTML_UNAUTHORIZED:
            raise OrbApiException("Unauthorized", error_codes.HTML_UNAUTHORIZED)
        elif connection.code == error_codes.HTML_BADREQUEST:
            json_resp = json.loads(connection.read())
            error = json.loads(json_resp["error"])
            if error["code"] == error_codes.ERROR_CODE_RESOURCETAG_EXISTS:
                if self.verbose_output:
                    print(error["message"])
                return
            else:
                raise OrbApiException(error["message"], error["code"])
                # pass
        elif connection.code == error_codes.HTML_SERVERERROR:
            raise OrbApiException("Connection or Server Error", error_codes.HTML_SERVERERROR)
        elif connection.code == error_codes.HTML_CREATED:
            # success
            resp = connection.read()
            data_json = json.loads(resp)
            return data_json

        return


# Comparability functions

def orb_resource():
    return OrbResource()


def orb_resource_file():
    return OrbResourceFile()


def orb_resource_url():
    return OrbResourceURL()


def orb_api(host='', username='', api_key=''):
    return OrbClient(
        host=host,
        username=username,
        api_key=api_key,
    )
