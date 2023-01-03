import json
import os
from urllib import response
import boto3

ddb = boto3.resource('dynamodb')
TABLE_NAME = os.environ['Table_Name']
#table = ddb.Table('website-visitors-count')
#_lambda = boto3.client('lambda')
table = ddb.Table(TABLE_NAME)

def handler(event, context):
    #table = ddb.Table(TABLE_NAME)
    print('request: {}'.format(json.dumps(event)))
    response = table.update_item(
        Key={'path': event['path']},
        UpdateExpression='ADD hits :incr',
        ExpressionAttributeValues={':incr': 1}
    )
    return response