import boto3
import json
from http.cookies import SimpleCookie
from boto3.dynamodb.conditions import Key, Attr
import time


dynamodb = boto3.resource('dynamodb')
student_table = dynamodb.Table('dynamo-tongue-student-prod')
auth_table = dynamodb.Table('dynamo-tongue-auth-prod')


def lambda_handler(event, context):
    # Auth check.
    try:
        cookie = SimpleCookie()
        cookie.load(event['headers']['cookie'])
        usn_cookie = cookie['usn'].value
        pid_cookie = cookie['pid'].value
        auth_res = auth_table.get_item(
            Key={'_netId': usn_cookie.upper()}
        )['Item']
        if auth_res and auth_res['_netId'] == usn_cookie.upper() and auth_res['pid'] == pid_cookie and auth_res['expires'] > int(time.time()):
            auth_res['uses'] += 1
            auth_table.put_item(
                Item=auth_res
            )
        else:
            raise ValueError()
    except:
        return {
            'statusCode': 403,
            'headers': {
                "Access-Control-Allow-Origin": 'https://nassau.network',
                "Access-Control-Allow-Methods": 'GET',
                "Access-Control-Allow-Credentials": 'true',
                "Access-Control-Allow-Headers": 'X-Cas-Ticket,x-cas-ticket'
            },
            'body': json.dumps({'message': '403 Forbidden'})
        }
    
    # Get the supplied parameters.
    params = event['pathParameters']
    net_id = params['netId']
    
    if net_id == "":
        return {
            'statusCode': 400,
            'body': json.dumps({'message': '400 Bad Request'})
        }
    
    # Get the student's information.
    response = student_table.get_item(
        Key={
            '_netId': net_id.upper()
        }
    )
    try:
        item = response['Item']
        # Filter out the index keys.
        item = {key: item[key] for key in item if not key.startswith('_')}
    except KeyError:
        return {
            'statusCode': 404,
            'body': json.dumps({'message': '404 Not Found'})
        }
        
    return {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Origin": 'https://nassau.network',
            "Access-Control-Allow-Methods": 'GET',
            "Access-Control-Allow-Credentials": 'true'
        },
        'body': json.dumps({'student': item})
    }
