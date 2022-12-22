import json
import boto3
from boto3.dynamodb.conditions import Key
from boto3.dynamodb.conditions import Attr
def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('liked')
    table.put_item(Item={'username':event['username'],'link':event['link'],'category':event['category']})
    
    message="Successfully liked post"
    return message
