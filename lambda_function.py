import logging
import json
import boto3
import base64
from botocore.client import Config
from customEncoder import CustomEncoder

logger = logging.getLogger()
logger.setLevel(logging.INFO)


getMethod = "GET"
healthPath = "/rekognition/health"


#main handler
def lambda_handler(event, context):

    logger.info(event)
    httpMethod = event['httpMethod']
    path = event['path']
    image_path = event['image_path']

    if httpMethod == getMethod and path == healthPath:

        rekognition = boto3.resource('rekognition')
        response = rekognition.Image(image_path).detect_labels()
        # labels = get_labels(response)
        
        labels = []
        for label in response['Labels']:
            labels.append(label['Name'])

        return buildResponse(200, labels)
    
    else:
        return buildResponse(404, 'Not Found')
    

# Response builder.
def buildResponse(statusCode, body = None):
    response = {
        'statusCode': statusCode,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }
    if body is not None:
        response['body'] = json.dumps(body, cls = CustomEncoder)
    return response