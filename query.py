import os

import boto3
from boto3.dynamodb.conditions import Key, Attr
import json


def _main():
    os.environ['AWS_PROFILE'] = 'tongue'

    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    student_table = dynamodb.Table('dynamo-tongue-student-prod')

    response = student_table.query(
        IndexName='_fname-index _lname-index',
        KeyConditionExpression=Key('_fname').eq('JOSEPH') & Key('_lname').eq('RUBIN')
    )

    print(response)


    exit(0)

    
    # Get the student's information.
    response = student_table.get_item(
        Key={
            'netId': net_id
        }
    )


if __name__ == '__main__':
    _main()
