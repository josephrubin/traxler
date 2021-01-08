import boto3
from http.cookies import SimpleCookie
from boto3.dynamodb.conditions import Key, Attr
import time
import json
import util as lib
import itertools


dynamodb = boto3.resource('dynamodb')
student_table = dynamodb.Table('dynamo-tongue-student-prod')
auth_table = dynamodb.Table('dynamo-tongue-auth-prod')

REPLACEMENTS = {
    'A': ['AH'],
    'C': ['K', 'CH'],
    'F': ['PH'],
    'G': ['J'],
    'H': [''],
    'I': ['EE', 'Y'],
    'J': ['G'],
    'K': ['C', 'CH'],
    'L': ['LL'],
    'O': ['OH'],
    'S': ['Z'],
    'V': ['PH'],
    'Y': ['I'],
    'Z': ['S'],
}


def lambda_handler(event, context):
    # Get the supplied parameters.
    params = event['queryStringParameters']
    
    try:
        q = str(params['q'])
        fast = (True if params['fast'] == "1" else False)
        count = int(params['count'])
        start = int(params['start'])
    except:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': '400 Bad Request'})
        }
    
    if q == "":
        return {
            'statusCode': 400,
            'body': json.dumps({'message': '400 Bad Request'})
        }
        
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
            if not fast:
                # Only count for one of the search types because the two happen at the same time
                # and because the update is not atomic, sometimes we would count one, and sometimes both.
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
        
    results = []    
    
    # Analyze `q`.
    # Our index is always upper case.
    q = q.upper()
    tokens = q.split(' ')
    
    if len(tokens) == 0:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': '400 Bad Request'})
        }
        
    # Only use the first 4 tokens for speed.
    too_many_tokens = False
    if len(tokens) > 4:
        too_many_tokens = True
        tokens = tokens[:4]
    
    if len(tokens) == 1:
        token = tokens[0]
        
        items = lib.query_as_netid(student_table, token)
        results.extend(items)
        
        items = lib.query_as_fname(student_table, token)
        results.extend(items)
        
        items = lib.query_as_lname(student_table, token)
        results.extend(items)
        
        if not fast:
            if len(token) <= 10:
                for i, c in enumerate(token):
                    if c in REPLACEMENTS:
                        for _c in REPLACEMENTS[c]:
                            _token = token[:i] + _c + token[i+1:]
                        
                            items = lib.query_as_fname(student_table, _token)
                            results.extend(items)
                            
                            items = lib.query_as_lname(student_table, _token)
                            results.extend(items)
        """
        # Scan operations are too slow.
        if not fast:
            items = lib.scan_as_fname(student_table, token)
            results.extend(items)
            
            items = lib.scan_as_lname(student_table, token)
            results.extend(items)
        """
            
    else:
        for token_one, token_two in itertools.combinations(tokens, 2):
            items = lib.query_as_fname_and_lname(student_table, token_one, token_two)
            results.extend(items)
            
        if not fast:
            for token in tokens:
                items = lib.query_as_netid(student_table, token)
                results.extend(items)
            
            for token in tokens:
                items = lib.query_as_fname(student_table, token)
                results.extend(items)
            
            for token in tokens:
                items = lib.query_as_lname(student_table, token)
                results.extend(items)
        
    # dedup
    seen = set()
    _results = []
    for result in results:
        if result['_netId'] not in seen:
            seen.add(result['_netId'])
            _results.append({key: result[key] for key in result if not key.startswith('_')})
        
    return {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Origin": 'https://nassau.network',
            "Access-Control-Allow-Methods": 'GET',
            "Access-Control-Allow-Credentials": 'true',
            "Access-Control-Allow-Headers": 'X-Cas-Ticket,x-cas-ticket'
        },
        'body': json.dumps({'students': _results, 'too_many_tokens': too_many_tokens})
    }
