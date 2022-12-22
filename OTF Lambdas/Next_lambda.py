import json
import boto3
from boto3.dynamodb.conditions import Key
from boto3.dynamodb.conditions import Attr
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
viewtable = dynamodb.Table('view')

def lambda_handler(event, context):
    print(event['username'])
    print(event)
    qname= event['username']+event['category']+'queue'
    print(qname)
    sqs = boto3.resource('sqs')
    sqs2 = boto3.client('sqs')
    queue=sqs2.get_queue_url(QueueName=qname)
    queueurl=queue['QueueUrl']
    response1=sqs2.receive_message(QueueUrl=queueurl)
    if 'Messages' not in response1:
        print("end")
        return "You have reached the end."
    final_response=json.loads(response1['Messages'][0]['Body'])
    viewtable.put_item(Item={'username':event['username'],'link':final_response['link'],'category':final_response['category']})
    if 'Messages' in response1:
        receipthandle=response1['Messages'][0]['ReceiptHandle']
        sqs2.delete_message(QueueUrl=queueurl,ReceiptHandle=receipthandle)
        
    
    return final_response