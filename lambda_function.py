import logging
import json
import boto3
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
    image = event['image']

    if httpMethod == getMethod and path == healthPath:
        # response = buildResponse(200)
        # yo do i put my code here ?
        rekognition = boto3.client('rekognition')
        image_bytes = event['image_bytes']
        response = rekognition.detect_labels(Image={'Bytes': image_bytes})
        labels = get_labels(response)

    else:
        response = buildResponse(404, 'Not Found')
    
    return response

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