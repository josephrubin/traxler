import os
from http.cookies import SimpleCookie
import time

import boto3


_DYNAMODB = boto3.resource('dynamodb')
_AUTHENTICATION_TABLE = _DYNAMODB.Table(os.environ['AUTHENTICATION_TABLE'])


def get_authentication_record(netid):
    """Find and return the record for the authentication of netid.

    Returns the record if it was found (even if it has expired), and
    None otherwise.
    """
    authentication_response_raw = _AUTHENTICATION_TABLE.get_item(
        Key={'_netid': netid.upper()}
    )

    if not authentication_response_raw:
        return None

    return authentication_response_raw['Item']


def validate(event):
    """Validate the credentials of the user, given their cookie.

    Returns true if the user is validated, and false otherwise.
    """
    # Localhost is not allowed to validate CAS tickets, meaning we'll have to
    # skip the auth table check, as there will never be a stored valid ticket there.
    # This is okay because locally deployed lambdas do not have access to the live
    # database unless you have the AWS creds for whatever database you are pointing
    # to on your local machine.
    # Thus running this code locally will not allow you to access more data than
    # you could have previously.
    # Funnily enough, while localhost can't validate tickets, localhost is an
    # approved login service, meaning the system will generate a CAS ticket for
    # the login if we wanted, we just can't check it!
    if 'localhost' in os.environ['WEBSITE_DOMAIN']:
        return True

    try:
        user_cookie = event['headers']['cookie']
    except KeyError:
        return False
    if not user_cookie or not type(user_cookie) is str:
        return False

    # Load the user's cookie to inspect their credentials.
    cookie = SimpleCookie()
    cookie.load(user_cookie)

    try:
        netid_cookie = cookie['netid'].value
        token_cookie = cookie['token'].value
    except KeyError:
        return False

    if not netid_cookie or not token_cookie:
        return False

    authentication_response = get_authentication_record(netid_cookie)
    if authentication_response                                        \
        and authentication_response['_netid'] == netid_cookie.upper() \
        and authentication_response['token'] == token_cookie          \
        and authentication_response['expires'] > int(time.time()):
        # The user is correctly authenticated, their request is valid.
        # Note that we also need to check authorization when we let users update
        # their accounts.

        # Increment the number of uses this user has. Note that we don't track
        # details about the use here, only an integer that tells us that there
        # was use. This increment is actually atomic since we use update_item!
        _AUTHENTICATION_TABLE.update_item(
            Key={'_netid': authentication_response['_netid']},
            UpdateExpression="set uses = uses + 1",
            ReturnValues="UPDATED_NEW"
        )
        return True

    return False
