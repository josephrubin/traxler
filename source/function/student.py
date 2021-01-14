import json
import os
import time

import boto3

import authentication
import response


_DYNAMODB = boto3.resource('dynamodb')
_STUDENT_TABLE = _DYNAMODB.Table(os.environ['STUDENT_INFORMATION_TABLE'])


def lambda_handler(event, context):
    # Authentication check before we do anything else.
    if not authentication.validate(event):
        return response.forbidden()

    # Get the supplied parameters.
    params = event['pathParameters']
    netid = params['netid']

    if netid == "":
        return response.bad_request()
    
    # Get the student's information.
    result = _STUDENT_TABLE.get_item(
        Key={
            '_netid': netid.upper()
        }
    )

    try:
        item = result['Item']
        # Filter out the index keys.
        item = {key: item[key] for key in item if not key.startswith('_')}
    except KeyError:
        return response.not_found()
        
    return response.okay(json.dumps({'student': item}))
