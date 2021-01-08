from http.cookies import SimpleCookie


_AUTHENTICATION_TABLE = dynamodb.Table(os.environ['AUTHENTICATION_TABLE'])


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


def validate(user_cookie):
    """Validate the credentials of the user, given their cookie.

    Returns true if the user is validated, and false otherwise.
    """
    if not user_cookie or not type(user_cookie) is str:
        return false

    # Load the user's cookie to inspect their credentials.
    cookie = SimpleCookie()
    cookie.load(user_cookie)

    netid_cookie = cookie['netid'].value
    token_cookie = cookie['token'].value

    # The cookies must be present.
    if not netid_cookie or not token_cookie:
        return false

    authentication_response = get_authentication_record(netid_cookie)
    if authentication_response                                        \
        and authentication_response['_netid'] == netid_cookie.upper() \
        and authentication_response['token'] == token_cookie          \
        and authentication_response['expires'] > int(time.time()):
        # The user is correctly authenticated, their request is valid.
        # Note that we also eed to check authorization when we let users update
        # their accounts.

        # Increment the number of uses this user has. Note that we don't track
        # details about the use here, only an integer that tells us that there
        # was use. This increment is actually atomic since we use update_item!
        _AUTHENTICATION_TABLE.update_item(
            Key={'_netid': authentication_response['_netid']},
            UpdateExpression="set uses = uses + 1",
            ReturnValues="UPDATED_NEW"
        )
        return true

    return false
