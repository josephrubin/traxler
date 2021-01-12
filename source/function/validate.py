import json
import os
import random
import re
import string
import time
import urllib.request

import boto3


_DYNAMODB = boto3.resource('dynamodb')
_AUTHENTICATION_TABLE = _DYNAMODB.Table(os.environ['AUTHENTICATION_TABLE'])

# The location of the service that validates a CAS ticket, letting us know if
# the user indeed logged in and was given that ticket.
# There are three parts:
# 1) Princeton's validation URL.
# 2) The ticket we are trying to validate (to be filled in a needed).
# 3) The place in our app to redirect to after attempting to validate.
#    Contains the parameter c=1 to let our app know that the login page was
#    reached from a CAS validation redirect and to continue if successfully
#    validated.
_CAS_VALIDATION_URL = 'https://fed.princeton.edu/cas/serviceValidate' \
                      '?ticket={}'                                    \
                      '&service=https://{}/login.html?c=1'

# Regex to get the user's netid from the cas response.
_NETID_PATTERN = re.compile(r'<cas:user>(.*?)<\/cas:user>')

# The alphabet from which to draw authentication tokens.
_ALPHABET = ''.join([c for c in string.ascii_letters + string.digits
                     if c not in 'aeiouAEIOU'])

# Number of seconds that the auth code is valid. After the duration, the user
# will be forced to get a new code by authenticating with CAS again.
# Currently: seven days.
_AUTH_DURATION = 60 * 60 * 24 * 7


def lambda_handler(event, context):
    headers = event['headers']
    ticket = headers['x-cas-ticket']
    
    # Make a request to validate the CAS ticket.
    validation_response = urllib.request.urlopen(
        _CAS_VALIDATION_URL.format(
            ticket,
            os.environ['WEBSITE_DOMAIN']
        )
    )
    validation_text = validation_response.read().decode('ascii')
    
    # Check if the validation was successful.
    if 'authenticationSuccess' not in text:
        return response.ok(
            json.dumps({"message": "Could not verify."}),
        )
    
    # There was an authentication success, so find the netid that logged in.
    netid = NETID_PATTERN.search(text).group(1)
    
    # We want to use the same ticket for many devices under the same user so
    # we can track uses in one place.
    # Check if the ticket is already there and valid:
    authentication_record = authentication.get_authentication_record(netid)

    if authentication_record and authentication_record['_netid'] == netid.upper():
        # We've found a (possibly invalid) authentication record for the user.
        # Store the uses count in case we need to create a new record.
        uses = authentication_record['uses']
        expires = authentication_record['expires']

        if expires > int(time.time()):
            # We've found a valid record, grab the existing ticket and return it
            # to the user.
            ticket = authentication_record['ticket']
            time_left = expires - int(time.time())
            
            return response.okay(
                json.dumps({"message": "Could verify."}),
                headers = {
                    # Add headers to set cookies on the user's browser. Using
                    # different capitalization allows us to set two cookies.
                    # Don't bother storing these cookies for longer than they will
                    # be valid from the server's point of view.
                    'Set-Cookie': 'ticket={}; Max-Age={}; Secure; HttpOnly'.format(ticket, time_left),
                    'set-Cookie': 'netid={}; Max-Age={}; Secure; HttpOnly'.format(netid, time_left),
                }
            )
    else:
        uses = 0

    # There either wasn't an old record, or it has expired.
    # Create a new ticket and add it to the authentication table.
    ticket = ''.join(random.choice(ALPHABET) for _ in range(24))
    _AUTHENTICATION_TABLE.put_item(
        Item={
            '_netid': netid.upper(),
            'ticket': ticket,
            'expires': int(time.time()) + AUTH_DURATION,
            'uses': uses
        }    
    )
    
    return response.okay(
        json.dumps({"message": "Could verify."}),
        headers = {
            # Add headers to set cookies on the user's browser. Using
            # different capitalization allows us to set two cookies.
            # Don't bother storing these cookies for longer than they will
            # be valid from the server's point of view.
            'Set-Cookie': 'ticket={}; Max-Age={}; Secure; HttpOnly'.format(ticket, AUTH_DURATION),
            'set-Cookie': 'netid={}; Max-Age={}; Secure; HttpOnly'.format(netid, AUTH_DURATION)
        }
    )
