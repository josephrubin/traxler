import boto3
from boto3.dynamodb.conditions import Key, Attr
import json
import random
import string
import urllib.request
import re
import time


dynamodb = boto3.resource('dynamodb')
auth_table = dynamodb.Table('dynamo-tongue-auth-prod')

NETID_PATTERN = re.compile(r'<cas:user>(.*?)<\/cas:user>')
ALPHABET = ''.join([c for c in string.ascii_letters + string.digits
                    if c not in 'aeiouAEIOU'])


# Number of seconds that the auth code is valid.
AUTH_DURATION = 604800


def lambda_handler(event, context):
    headers = event['headers']
    ticket = headers['x-cas-ticket']
    
    # Validate the CAS ticket.
    VALIDATE_URL = 'https://fed.princeton.edu/cas/serviceValidate?ticket={}&service=https://nassau.network/login.html?c=1'
    res = urllib.request.urlopen(VALIDATE_URL.format(ticket))
    text = res.read().decode('ascii')
    
    if 'authenticationSuccess' not in text:
        return {
            'statusCode': 200,
            'headers': {
            "Access-Control-Allow-Origin": 'https://nassau.network',
            "Access-Control-Allow-Methods": 'POST',
            "Access-Control-Allow-Credentials": 'true',
            'Cache-Control': 'no-store'
            },
            'body': json.dumps({"message": "Could not verify."})
        }
    
    net_id = NETID_PATTERN.search(text).group(1)
    
    # We want to use the same pid for many devices under the same user.
    # Check if the pid is already there and valid:
    auth_res = auth_table.get_item(
        Key={'_netId': net_id.upper()}
    )
    starting_uses = 0
    found_auth = False
    if 'Item' in auth_res:
        auth_res = auth_res['Item']
        if auth_res['uses']:
            starting_uses = auth_res['uses']
        found_auth = True
    if found_auth and auth_res['_netId'] == net_id.upper() and auth_res['expires'] > int(time.time()):
        # The pid is there and valid. Simply grab the existing pid to return to the user.
        pid = auth_res['pid']
    else:
        # Create a new pid and add it to the auth table.
        pid = ''.join(random.choice(ALPHABET) for _ in range(24))
        auth_table.put_item(
            Item={
                '_netId': net_id.upper(),
                'pid': pid,
                'expires': int(time.time()) + AUTH_DURATION,
                'uses': starting_uses
            }    
        )
    
    return {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Origin": 'https://nassau.network',
            "Access-Control-Allow-Methods": 'POST',
            "Access-Control-Allow-Credentials": 'true',
            'Set-Cookie': 'pid={}; Max-Age={}; Secure; HttpOnly'.format(pid, AUTH_DURATION),
            'set-Cookie': 'usn={}; Max-Age={}; Secure; HttpOnly'.format(net_id, AUTH_DURATION),
            'Cache-Control': 'no-store'
        },
        'body': json.dumps({"message": "Could verify."})
    }
