import itertools
import json
import os
import time

import boto3
from boto3.dynamodb.conditions import Key, Attr
from http.cookies import SimpleCookie

import authentication
import response
import search_util as lib


_DYNAMODB = boto3.resource('dynamodb')
_STUDENT_TABLE = _DYNAMODB.Table(os.environ['STUDENT_INFORMATION_TABLE'])

# Common mispellings that allow us to search for intended results.
_REPLACEMENTS = {
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
    # Authentication check before we do anything else.
    if not authentication.validate(event):
        return response.forbidden()

    # Get the supplied parameters.
    params = event['queryStringParameters']
    try:
        # The user's query.
        q = str(params['q'])
        if not q:
            return response.bad_request()
        # True to quickly return results, false to do a slower search to find
        # more results (always a superset of fast=True results).
        fast = (True if params['fast'] == '1' else False)
    except:
        return response.bad_request()
        
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
        
        items = lib.query_as_netid(_STUDENT_TABLE, token)
        results.extend(items)
        
        items = lib.query_as_fname(_STUDENT_TABLE, token)
        results.extend(items)
        
        items = lib.query_as_lname(_STUDENT_TABLE, token)
        results.extend(items)
        
        if not fast:
            if len(token) <= 10:
                for i, c in enumerate(token):
                    if c in _REPLACEMENTS:
                        for _c in _REPLACEMENTS[c]:
                            _token = token[:i] + _c + token[i+1:]
                        
                            items = lib.query_as_fname(_STUDENT_TABLE, _token)
                            results.extend(items)
                            
                            items = lib.query_as_lname(_STUDENT_TABLE, _token)
                            results.extend(items)
        """
        # Scan operations are too slow.
        if not fast:
            items = lib.scan_as_fname(_STUDENT_TABLE, token)
            results.extend(items)
            
            items = lib.scan_as_lname(_STUDENT_TABLE, token)
            results.extend(items)
        """
            
    else:
        for token_one, token_two in itertools.combinations(tokens, 2):
            items = lib.query_as_fname_and_lname(_STUDENT_TABLE, token_one, token_two)
            results.extend(items)
            
        if not fast:
            for token in tokens:
                items = lib.query_as_netid(_STUDENT_TABLE, token)
                results.extend(items)
            
            for token in tokens:
                items = lib.query_as_fname(_STUDENT_TABLE, token)
                results.extend(items)
            
            for token in tokens:
                items = lib.query_as_lname(_STUDENT_TABLE, token)
                results.extend(items)
        
    # Deduplicate the results and remove all properties that start with
    # underscore (as these are our table keys in uppercase). Use a list the
    # whole time to preserve ordering.
    seen_netids = set()
    results_curated = []
    for result in results:
        if result['_netid'] not in seen_netids:
            results_curated.append({
                key: result[key] for key in result if not key.startswith('_')
            })
        
    return response.okay(
        json.dumps({
            'students': results_curated,
            'too_many_tokens': too_many_tokens
        })
    )
