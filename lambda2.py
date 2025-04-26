import boto3
import json
import os
import requests
import uuid
from decimal import Decimal


s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('PlantIdentifications')

def lambda_handler(event, context):

    print("Event:", event)

    # 1. Get bucket and image key from S3 event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    image_key = event['Records'][0]['s3']['object']['key']
    image_name = image_key.split('/')[-1]

    # 2. Read image content from S3
    response = s3.get_object(Bucket=bucket_name, Key=image_key)
    image_content = response['Body'].read()  

    # 3. Send image to Plant.id API
    plant_id_api_key = "  "  #enter your api key
    files = {'images': ('image.jpg', image_content, 'image/jpeg')}

    res = requests.post(
        'https://plant.id/api/v3/identification', #API URL 
        files=files,
        headers={'Api-Key': plant_id_api_key}
    )

    print("API Response:", res.text)

    try:
        plant_name = res.json()['result']['classification']['suggestions'][0]['name']
        probability = res.json()['result']['classification']['suggestions'][0]['probability']
        if probability > 0.5:
            is_plant = True
        else:
            is_plant = False
    except Exception as e:
        print("Error parsing result:", e)
        plant_name = "Unknown"

    # 4. Save result to DynamoDB
    table.put_item(
        Item={
            'id': str(uuid.uuid4()),
            'imageName': image_name,
            'plantName': plant_name,
            'probability': Decimal(str(probability)),
            'is_plant': is_plant
        }
    )

    print('Upload success')

    return {
        'statusCode': 200,
        'body': json.dumps(f'Plant identified: {plant_name}')
    }



