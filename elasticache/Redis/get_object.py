# Copyright 2010-2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# This file is licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License. A copy of the
# License is located at
#
# http://aws.amazon.com/apache2.0/
#
# This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
import logging
import time
import redis
from botocore.exceptions import ClientError


def get_object(client, key):
    """Retrieve an object from configured redis under specified key

    :param endpoint: string
    :param key: string
    :return: string. If error, return None.
    """
    # Connect to redis
    #r = redis.Redis(host=endpoint, port=6379, db=0)
    # Retrieve the object
    response = client.get(name=key)
    return response

def get_object_or_wait(client, key, sleep_time):
    """Retrieve an object from configured redis under specified key

    :param endpoint: string
    :param key: string
    :return: numpy arrary. If error, return None.
    """
    # Connect to redis
    #client = redis.Redis(host=endpoint, port=6379, db=0)
    # Retrieve the object
    while True:
        response = client.get(name=key)
        if response != None:
            return response
        time.sleep(sleep_time)
    


def hget_object(client, key,field):
    """Retrieve an object from configured redis under specified key

    :param endpoint: string
    :param key: string
    :param field: string
    :return: string. If error, return None.
    """
    # Connect to redis
    #client = redis.Redis(host=endpoint, port=6379, db=0)
    # Retrieve the object
    
    response = client.hget(name = key,key = field)
   
    return response

def hget_object_or_wait(client, key, field, sleep_time):
    """Retrieve an object from configured redis under specified key

    :param endpoint: string
    :param key: string
    :param field: string
    :return: numpy arrary. If error, return None.
    """
    # Connect to redis
    #client = redis.Redis(host=endpoint, port=6379, db=0)
    # Retrieve the object

    while True:
        response = client.hget(name=key, key = field)
        if response != None:
            return response
        time.sleep(sleep_time)



def handler(event, context):
    endpoint = redis.Redis(host="test-001.fifamc.0001.euc1.cache.amazonaws.com",port=6379,db=0)
    key = "lambdaml"
    print(get_object(endpoint,key))
