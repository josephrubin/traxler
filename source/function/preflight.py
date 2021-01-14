"""Support CORS preflight requests, returning CORS headers on OPTIONS requests."""
import json

import response


def lambda_handler(event, context):
    return response.okay(json.dumps({}))