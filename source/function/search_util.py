import json

import boto3
from boto3.dynamodb.conditions import Key, Attr


def scan_as_fname(table, token):
    return table.scan(
                FilterExpression=Attr('_fname').contains(token)
            )['Items']
            
def scan_as_lname(table, token):
    return table.scan(
                FilterExpression=Attr('_lname').contains(token)
            )['Items']

def query_as_netid(table, token):
    return table.query(
                KeyConditionExpression=Key('_netid').eq(token)
            )['Items']

def query_as_fname(table, token):
    return table.query(
                IndexName='_fname-_lname-index',
                KeyConditionExpression=Key('_fname').eq(token)
            )['Items']

def query_as_lname(table, token):
    return table.query(
                IndexName='_lname-_fname-index',
                KeyConditionExpression=Key('_lname').eq(token)
            )['Items']
            
def query_as_fname_and_lname(table, token_one, token_two):
    part_one = [res for res in table.query(
                IndexName='_fname-_lname-index',
                KeyConditionExpression=Key('_fname').eq(token_one)
            )['Items']
                #if token_two in res['_lname']
                if fuzzy_in(token_two, res['_lname'])
            ]
            
    part_two = [res for res in table.query(
                IndexName='_lname-_fname-index',
                KeyConditionExpression=Key('_lname').eq(token_one)
            )['Items']
                #if token_two in res['_fname']
                if fuzzy_in(token_two, res['_fname'])
            ]
            
    part_three = [res for res in table.query(
                IndexName='_fname-_lname-index',
                KeyConditionExpression=Key('_fname').eq(token_two)
            )['Items']
                #if token_one in res['_lname']
                if fuzzy_in(token_one, res['_lname'])
            ]
            
    part_four = [res for res in table.query(
                IndexName='_lname-_fname-index',
                KeyConditionExpression=Key('_lname').eq(token_two)
            )['Items']
                #if token_one in res['_fname']
                if fuzzy_in(token_one, res['_fname'])
            ]
            
    return part_one + part_two + part_three + part_four
    
    
def fuzzy_in(string_one, string_two, thresh=4):
    """Check if a good number of characters from string_one are in string_two in order."""
    threshold = min(len(string_one), thresh)
    match_count = 0
    last_match_index = -1
    for i, c in enumerate(string_one):
        # Optimize: break out if no chance.
        if match_count + len(string_one) - i < threshold:
            return False
        idx = string_two.find(c, last_match_index + 1)
        if idx != -1:
            match_count += 1
            last_match_index = idx
    return match_count >= threshold
