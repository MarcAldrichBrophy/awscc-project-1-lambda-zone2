import logging
import json
import boto3
import base64
import io
import imghdr
import uuid
from botocore.client import Config
from customEncoder import CustomEncoder

logger = logging.getLogger()
logger.setLevel(logging.INFO)
s3 = boto3.client('s3')


getMethod = "GET"
healthPath = "/rekognition/health"
rekognition = boto3.client('rekognition')

def get_labels(response):
    labels = []
    #bucket can only hold up to 10 labels!
    size = len(response['Labels'])
    if size > 10:
        for i in range(10):
            label = response['Labels'][i]
            if (float(label['Confidence']) >= 75):
                labels.append(label['Name'])
                labels.append(label['Confidence'])
        return labels
    else:
        for label in response['Labels']:
            if (float(label['Confidence']) >= 75):
                labels.append(label['Name'])
                labels.append(label['Confidence'])
        return labels


#main handler
def lambda_handler(event, context):

    logger.info(event)
    httpMethod = event['httpMethod']
    path = event['path']
    image_base64 = event['imageBase64']

    if httpMethod == getMethod and path == healthPath:

        #decode image
        image_data = base64.b64decode(image_base64)

        #convert image
        image = {'Bytes': image_data}

        #run rekognition detect_labels API
        response = rekognition.detect_labels(Image={'Bytes': image_data})
        #detect text
        textResponse = rekognition.detect_labels(Image={'Bytes': image_data})

        #get text
        text = textResponse['TextDetections']
        result['text'] = text


        labels = get_labels(response)
        result = {'labels': labels}

        labels_json = json.dumps(labels)


        #S3 UPLOAD:

        #detect file type
        image_type = imghdr.what(None, h = image_data)
        if image_type == 'jpeg':
            file_ext = '.jpeg'
        elif image_type == 'png':
            file_ext = '.png'

        #generate key
        key = uuid.uuid4().hex + file_ext

        #upload image
        s3.upload_fileobj(
            Fileobj = io.BytesIO(image_data),
            Bucket = 'project-1-datalake',
            Key = key,
        )

        #add tags to image
        s3.put_object_tagging(
            Bucket = 'project-1-datalake',
            Key = key,
            Tagging = {'TagSet': [
                    {'Key': label, 'Value': str(confidence)} 
                    for label, confidence in zip(labels[::2], labels[1::2])
                ]
            }
        )

        return buildResponse(200, result)
    
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