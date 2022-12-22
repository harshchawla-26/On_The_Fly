
import json
import boto3
import datetime
import requests
from decimal import *
import urllib.parse
from time import sleep
client = boto3.resource(service_name='dynamodb',
                          region_name="us-east-1",
                         )
table = client.Table('news')
def lambda_handler(event,context):
    categories=['sports','science','business','technology','entertainment']

    for category in categories:

            params = urllib.parse.urlencode({
            'country':'us',
            'apiKey': 'pub_142931cab2a257311247a4dc0cc3639efb7e8',
            'category': category,

            'language':'en',
            'page':1,
            })
            response = requests.get("https://newsdata.io/api/1/news?", params=params)
            js = response.json()
            addItems(js["results"], category)
            sleep(0.001)

def addItems(data, category):

   with table.batch_writer() as batch:
        for rec in data:
            try:
                if (rec["content"] is None or len(str(rec['content']))<700):
                    continue;
                    
                rec['category'] = category

                rec.pop("keywords", None)
                rec.pop("creator", None)
                rec.pop("video_url", None)
                rec.pop("description", None)
                rec.pop("pubDate", None)
                rec.pop("image_url", None)
                rec.pop("source_id", None)
                rec.pop("language", None)
                rec.pop("country", None)
                batch.put_item(Item=rec)


                sleep(0.001)
            except Exception as e:
                print(e)
                print(rec)