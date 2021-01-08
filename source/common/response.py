import os


_CORS_HEADERS = {
    # Allow the domain hosting the site to make requests to this API.
    'Access-Control-Allow-Origin': 'https://{}'.format(os.environ['WEBSITE_DOMAIN']),
    'Access-Control-Allow-Methods': 'GET,POST',
    # Allow the cas ticket header for authentication.
    'Access-Control-Allow-Headers': 'x-cas-ticket',
    # Allow cookeis to be sent with requests.
    'Access-Control-Allow-Credentials': 'true'
}


def okay(body, *, headers={}):
    """Return a 200 okay response with CORS headers."""
    return {
        'statusCode': 200,
        'headers': {**_CORS_HEADERS, **headers},
        'body': 'body'
    }


def not_found():
    """Return a 404 not found response with CORS headers."""
    return {
        'statusCode': 404,
        'headers': _CORS_HEADERS,
        'body': '{"message": "Not Found"}'
    }


def bad_request():
    """Return a 400 bad request response with CORS headers."""
    return {
        'statusCode': 400,
        'headers': _CORS_HEADERS,
        'body': '{"message": "Bad Request"}'
    }


def forbidden():
    """Return a 403 forbidden response with CORS headers."""
    return {
        'statusCode': 403,
        'headers': _CORS_HEADERS,
        'body': '{"message": "Forbidden"}'
    }
