from django.shortcuts import render
from django.http import HttpResponse

from contextlib import closing
import csv
from io import StringIO
import io

from django.db import connection
from django.utils import timezone
from django.conf import settings
import os
import time

from collections import defaultdict
from django.apps import apps

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from . import models
import requests

import logging
logger = logging.getLogger(__name__)

class BulkCreateManager(object):
    """
    This helper class keeps track of ORM objects to be created for multiple
    model classes, and automatically creates those objects with `bulk_create`
    when the number of objects accumulated for a given model class exceeds
    `chunk_size`.
    Upon completion of the loop that's `add()`ing objects, the developer must
    call `done()` to ensure the final set of objects is created for all models.
    """

    def __init__(self, chunk_size=10000):
        self._create_queues = defaultdict(list)
        self.chunk_size = chunk_size

    def _commit(self, model_class):
        model_key = model_class._meta.label
        model_class.objects.bulk_create(self._create_queues[model_key])
        self._create_queues[model_key] = []

    def add(self, obj):
        """
        Add an object to the queue to be created, and call bulk_create if we
        have enough objs.
        """        
        model_class = type(obj)
        model_key = model_class._meta.label
        self._create_queues[model_key].append(obj)
        if len(self._create_queues[model_key]) >= self.chunk_size:
            self._commit(model_class)

    def done(self):
        """
        Always call this upon completion to make sure the final partial chunk
        is saved.
        """
        for model_name, objs in self._create_queues.items():
            if len(objs) > 0:
                self._commit(apps.get_model(model_name))    



def index(request):
    return render(request, 'bulkload/index.html')

def results(request):
    return render(request, 'bulkload/results.html')



"""
Main routine for bulkloading the db with Postgres copy_from utility from a csv file
1. Get the data to load in json format
2. Write json data to a csv file
3. Read the csv file and bulkload the data into the db
"""
def copy_from(request):
    logger.debug("In Postgres copy_from")
   
    json = get_json_response()
    write_json_to_csvfile(json)
    start = time.time()
    postgres_bulkload_from_csvfile()
    end = time.time()
    
    count = models.Speaker.objects.count()
    duration = end - start
    logger.debug ("duration in seconds: " + str(duration))    
    models.Speaker.objects.all().delete()
    result = "Created " + str(count)   + " rows in " + str(duration * 1000) + " milliseconds"
    logger.debug(result)
    return render(request, 'bulkload/results.html', {'result': result}) 
 
    
"""
Main routine for bulkloading the db with Django bulk_create from a csv file
1. Get the data to load in json format
2. Write json data to a csv file
3. Read the csv file and bulkload the data into the db
"""
def bulk_create(request):
    logger.debug("In Django bulk_create")     
             
    json = get_json_response()
    write_json_to_csvfile(json)
    start = time.time()
    django_bulkload_from_csvfile()
    end = time.time()
    
    count = models.Speaker.objects.count()
    duration = end - start
    logger.debug ("duration in seconds: " + str(duration))    
    models.Speaker.objects.all().delete()
    result = "Created " + str(count)   + " rows in " + str(duration * 1000) + " milliseconds"
    logger.debug(result)
    return render(request, 'bulkload/results.html', {'result': result})

def postgres_bulkload_from_csvfile():
    stream = open("speakers.csv", "r", encoding="utf-8")
    stream.seek(0)
    with closing(connection.cursor()) as cursor:
        cursor.copy_from(
            file=stream,
            table='speakers',
            sep=',',
            columns=('first_name', 'last_name', 'title', 'company', 'speaker_bio', 'speaker_photo'),
        )
    
def django_bulkload_from_csvfile():
    stream = open("speakers.csv", "r", encoding="utf-8")
    stream.seek(0)
    
    with open("speakers.csv", 'rb') as csv_file:   
        bulk_mgr = BulkCreateManager(chunk_size=10000)
        start = time.time()
        try:
            for row in csv.reader(stream):
                bulk_mgr.add(models.Speaker(first_name=row[0], 
                            last_name=row[1],
                            title=row[2],
                            company=row[3],
                            speaker_bio=row[4],
                            speaker_photo=row[5].encode("utf-8"),))

        except Exception as e: 
            logger.debug("Error while importing data: " + e)      
        bulk_mgr.done()

def write_json_to_csvfile(json): 
        with open("speakers.csv", "w", newline='', encoding="utf-8") as csvfile:
            f = csv.writer(csvfile)            
            for elem in json:
                f.writerow([elem["first_name"], 
                            elem["last_name"], 
                            elem["title"], 
                            elem["company"], 
                            elem["speaker_bio"], 
                            elem["speaker_photo"],
                         ])
 
def get_json_response():
    
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.get('http://localhost:8088/conference/speakers', headers=headers)
        num_records = response.json()["count"] 
        offset = str(0)
        logger.debug("num_records: " + str(num_records))
        logger.debug("offset: " + offset)
        query = {'limit':num_records, 'offset':offset}
        response = requests.get('http://localhost:8088/conference/speakers', headers=headers, params=query)
        #logger.debug("Response back: " + response.text)
        logger.debug("Response.headers: " + str(response.headers))
        logger.debug("Response.status_code: " + str(response.status_code))
        
        if response.status_code == 200:
            logger.debug('Got speakers back, success!!!')
            json = response.json()["results"]   
            return json
        else:
            print('Status code is not 200 OK')
            logger.error('ErrorCode returned from invoking the speakers service', response.status_code)                      
            return render(request, 'bulkload/results.html', {'result': response.__str__()})
    except Exception as exec:  
        logger.error(exec.__str__())
        print('Caught Exception while retrieving speakers ' + exec.__str__()) 
        return render(request, 'bulkload/results.html', {'result': exec.__str__()})
