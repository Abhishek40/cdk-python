from __future__ import print_function
import os
from urllib import response
import boto3
import json
from botocore.exceptions import ClientError

ddb = boto3.resource('dynamodb')
TABLE_NAME = os.environ['Table_Name']
table = ddb.Table(TABLE_NAME)

def handler(event, context):
    response = table.scan()
    for i in response['Items']:
        return i