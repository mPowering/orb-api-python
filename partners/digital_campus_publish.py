#!/usr/bin/python
import argparse
import glob
import os
import re
import shutil
import sys

import MySQLdb
import MySQLdb.cursors

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_PATH = os.path.normpath(os.path.join(BASE_DIR, '..', 'orb_api'))

if PROJECT_PATH not in sys.path:
    sys.path.append(PROJECT_PATH)

MOODLE_BACKUP_DIR = "/home/alex/data/backup/aws/dc/courses/"
OUTPUT_DIR_BASE = "/home/alex/data/Digital-Campus/content-dev/share/"
IMAGE_DIR_BASE = "/home/alex/data/Digital-Campus/content-dev/images/"

MPOWERING_DEFAULT_TAGS = ["Digital Campus",
                          "Course",
                          "Community Health Worker",
                          "Midwife",
                          "Nurse",
                          "Africa",
                          "Global",
                          "Ethiopia",
                          "English",
                          "Laptop",
                          "Smartphone",
                          "Tablet",
                          "Creative Commons 2.0 (CC-BY-NC-SA)"]

DEBUG = True

from api import orb_api, orb_resource, orb_resource_file, orb_resource_url, ORBAPIResourceExistsException


def run(orb_url, orb_username, orb_key, db_name, db_user, db_passwd, update_files):
    api = orb_api()
    api.base_url = orb_url
    api.user_name = orb_username
    api.api_key = orb_key
    api.verbose_output = DEBUG

    db = MySQLdb.connect(host="localhost",
                         user=db_user,
                          passwd=db_passwd,
                          db=db_name)

    db.autocommit(True)

    # you must create a Cursor object. It will let
    #  you execute all the queries you need
    cur = db.cursor(MySQLdb.cursors.DictCursor)

    if update_files == 'True':
        '''
        Update with the most recent Moodle backup versions
        '''
        cur.execute("SELECT f.id, course_id, f.description, file, moodle_course_id, type, short_name, c.location_code FROM dc_file f INNER JOIN dc_course c ON c.id = f.course_id")
        for row in cur.fetchall():
            course_backups = glob.glob(MOODLE_BACKUP_DIR+'backup-moodle2-course-'+str(row['moodle_course_id'])+'-*.mbz')
            course_backups.sort()
            file_name = course_backups[len(course_backups)-1]
            file_date = re.findall(r'[0-9]{8}', file_name)

            old_course_backups = glob.glob(os.path.join(OUTPUT_DIR_BASE, row['location_code'], 'moodle-backups', row['short_name'] + '-' + row['type'] + '*.mbz'))
            for old_file in old_course_backups:
                if DEBUG:
                    print "Removing: " + old_file
                os.remove(old_file)

            new_file_name = row['short_name'] + "-" + row['type'] + "-" + file_date[0] +".mbz"
            if DEBUG:
                print "Copying over: " + new_file_name
            shutil.copy2(file_name, os.path.join(OUTPUT_DIR_BASE, row['location_code'], 'moodle-backups', new_file_name))

            #cur2 = db.cursor(MySQLdb.cursors.DictCursor)
            cur.execute("""UPDATE dc_file SET file = '%s' WHERE id = %s """ % (new_file_name, int(row['id'])))

    '''
    Publish updates to the mPowering
    '''
    cur.execute("""SELECT id, title, description, icon, tags, location_code, study_hours FROM dc_course WHERE mpowering = 1 """)

    additional_desc = "<p>This course is part of the Ethiopia Federal Ministry of Health approved upgrade training program for Health Extension Workers.</p>"

    # print all the first cell of all the rows
    for row in cur.fetchall() :

        resource = orb_resource()
        resource.title =  row['title'].decode('utf-8')
        resource.description = row['description'].decode('utf-8') + additional_desc
        if row['study_hours'] != None:
            resource.study_time_number = row['study_hours']
            resource.study_time_unit = 'hours'

        try:
            resource.id = api.add_resource(resource)
        except ORBAPIResourceExistsException, e:
            if DEBUG:
                print e.message + ", id no:" + str(e.pk)
            resource.id = e.pk
            # upate the resource
            api.update_resource(resource)

        if row['icon']:
            api.add_or_update_resource_image(resource.id, os.path.join(IMAGE_DIR_BASE, row['icon']))

        # get the resource id
        resource_from_api = api.get_resource(resource)

        # remove all ResourceFiles
        api.delete_resource_files(resource_from_api['files'])

        # remove all ResourceURLs
        api.delete_resource_urls(resource_from_api['urls'])

        # remove all tags for resource
        api.delete_resource_tags(resource_from_api['tags'])

        # add all the default tags
        for tag in MPOWERING_DEFAULT_TAGS:
            api.add_resource_tag(resource.id, tag.strip())

        # add resource specific tags
        if row['tags']:
            tag_list = [x.strip() for x in row['tags'].split(',')]
            for tag in tag_list:
                api.add_resource_tag(resource.id, tag.strip())

        # add the files
        cur.execute("""SELECT * FROM dc_file WHERE course_id = %s """ % (row['id']))
        for file in cur.fetchall():
            resource_file = orb_resource_file()
            resource_file.title = file['title']
            resource_file.description = file['description']
            resource_file.order_by = file['orderby']
            resource_file.file = os.path.join(OUTPUT_DIR_BASE, row['location_code'], 'moodle-backups', file['file'])
            api.add_resource_file(resource.id,resource_file)

        # add the urls
        cur.execute("""SELECT * FROM dc_url WHERE course_id = %s """ % (row['id']))
        for url in cur.fetchall():
            resource_url = orb_resource_url()
            resource_url.title = url['title']
            resource_url.description = url['description']
            resource_url.order_by = url['orderby']
            resource_url.url = url['url']
            api.add_resource_url(resource.id,resource_url)

    cur.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("orb_url", help="ORB url")
    parser.add_argument("orb_username", help="ORB User Name")
    parser.add_argument("orb_key", help="ORB API Key")
    parser.add_argument("db_name", help="Database name")
    parser.add_argument("db_user", help="Database user name")
    parser.add_argument("db_passwd", help="Database password")
    parser.add_argument("update_files", help="Update files True/False")
    args = parser.parse_args()
    run(args.orb_url, args.orb_username, args.orb_key, args.db_name, args.db_user, args.db_passwd, args.update_files)