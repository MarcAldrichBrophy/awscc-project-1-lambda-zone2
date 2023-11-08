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

        s3 = boto3.client('s3')

        bucket = 'project-1-code-zone2'
        key = 'image.PNG'

        s3.download_file(bucket, key, '/tmp/image.PNG')

        with open('/tmp/image.PNG', 'rb') as f:
            # if base64: image_bytes = base64.b64encode(image_file.read()).decode('utf-8')
            image_bytes = f.read()

        rekognition = boto3.client('rekognition')
        response = rekognition.detect_labels(Image={'Bytes': image_bytes})
        labels = get_labels(response)

        os.remove('/tmp/image.PNG')

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