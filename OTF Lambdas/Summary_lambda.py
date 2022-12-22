import os
import io
import boto3
import json
import csv
from time import sleep

def lambda_handler(event, context):
    
    ENDPOINT_NAME = os.environ['ENDPOINT_NAME']
    client= boto3.client('runtime.sagemaker')
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('news')
    sumtable = dynamodb.Table('summary')
    resp = table.scan()
    with sumtable.batch_writer() as batch:
        for item in resp['Items']:
            print(item)
            item['link']=item['link']
            item['title']=item['title']
            item['category']=item['category']
            if(len(str(item['content']))>2300):
                item['content']=item['content'][0:2300]
            payload = {'inputs':item['content']}
            response = client.invoke_endpoint(
            EndpointName=ENDPOINT_NAME,
            ContentType="application/json",
            Accept="application/json",
            Body=json.dumps(payload),
            )
            
            response = json.loads(response['Body'].read().decode())
            item['content']=response[0]['summary_text']
            batch.put_item(Item=item)
            sleep(0.001)
    return 0