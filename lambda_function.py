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

    if httpMethod == getMethod and path == healthPath:

        # yo do i put my code here ?
        with open('\image.PNG', 'rb') as image_file: #CHANGE THIS DIRECTORY LATER, upload image to S3 Bucket?
            image_bytes = base64.b64encode(image_file.read()).decode('utf-8')

        rekognition = boto3.client('rekognition')
        response = rekognition.detect_labels(Image={'Bytes': image_bytes})
        labels = get_labels(response)

        return buildResponse(200)
    
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