import json
import boto3

from boto3.dynamodb.conditions import Key
from boto3.dynamodb.conditions import Attr
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('summary')
viewtable = dynamodb.Table('view')

def lambda_handler(event, context):
    qname= event['username']+event['category']+'queue'
    cat=event['category']
    
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    liketable = dynamodb.Table('liked')
    table = dynamodb.Table('summary')
    viewtable = dynamodb.Table('view')
    sqs = boto3.resource('sqs')
    sqs2 = boto3.client('sqs')
    try:
        queue=sqs.get_queue_url(QueueName=qname)
        
    except:
        queue=sqs2.create_queue(QueueName=qname)
    queueurl=sqs2.get_queue_url(QueueName=qname)
    queueurl = queueurl['QueueUrl']
    
    resp = liketable.scan(FilterExpression=Attr('username').eq(event['username']))

    if(resp['Count']==0):
        return "No posts liked yet to create recommended feed."
    freq = {}
    for item in resp['Items']:
        if (item['category'] in freq):
            freq[item['category']] += 1
        else:
            freq[item['category']] = 1
 
    for key, value in freq.items():
        print ("% s : % d"%(key, value))
    cat=[] 
    
    if(len(freq)==1):
        return "Like a few more posts for a recommended feed."
    else:
        for i in range(2):
            inverse = [(value, key) for key, value in freq.items()]
            s=max(inverse)[1]
            cat.append(s)
            freq[s]=0
    print(cat)
    resp1 = table.scan(FilterExpression=Attr('category').eq(cat[0])|Attr('category').eq(cat[1]))
    j=0
    for i in resp1['Items']:
        print(resp)
        if(j==10):
            break
        x=viewtable.scan(FilterExpression=Attr('username').eq(event['username'])&Attr('link').eq(i['link']))
        if(x['Count']==0):     
            print("")
            response = sqs2.send_message(
                QueueUrl=queueurl,
                MessageBody=json.dumps(i)
            )
            j+=1
        else:
            continue
           
            
    response1=sqs2.receive_message(QueueUrl=queueurl)
    final_response=json.loads(response1['Messages'][0]['Body'])
    print(final_response)
    viewtable.put_item(Item={'username':event['username'],'link':final_response['link'],'category':final_response['category']})
    if 'Messages' in response1:
        receipthandle=response1['Messages'][0]['ReceiptHandle']
        sqs2.delete_message(QueueUrl=queueurl,ReceiptHandle=receipthandle)
        
    
    return final_response