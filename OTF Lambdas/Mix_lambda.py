import json
import boto3
from boto3.dynamodb.conditions import Key
from boto3.dynamodb.conditions import Attr
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('summary')
viewtable = dynamodb.Table('view')
def lambda_handler(event, context):
    qname= event['username']+event['category']+'queue'
    sqs = boto3.resource('sqs')
    sqs2 = boto3.client('sqs')
    try:
        queue=sqs.get_queue_url(QueueName=qname)
        print(sqs2.get_queue_url(QueueName=qname))
    except:
        queue=sqs2.create_queue(QueueName=qname)
    queueurl=sqs2.get_queue_url(QueueName=qname)
    queueurl = queueurl['QueueUrl']
    resp = table.scan()
    for i in resp['Items']:
        x=viewtable.scan(FilterExpression=Attr('username').eq(event['username'])&Attr('link').eq(i['link']))
        print(x)
        if(x['Count']==0):     
            print("pushing queue")
            response = sqs2.send_message(
                QueueUrl=queueurl,
                MessageBody=json.dumps(i)
            )
        else:
            continue
    response1=sqs2.receive_message(QueueUrl=queueurl)
    final_response=json.loads(response1['Messages'][0]['Body'])
    viewtable.put_item(Item={'username':event['username'],'link':final_response['link'],'category':i['category']})
    if 'Messages' in response1:
        receipthandle=response1['Messages'][0]['ReceiptHandle']
        sqs2.delete_message(QueueUrl=queueurl,ReceiptHandle=receipthandle)
        
    
    return final_response


