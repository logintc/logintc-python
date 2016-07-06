"""
The LoginTC Python client is a complete LoginTC REST API client to manage
LoginTC organizations, users, domains, tokens and to create login sessions.

Further documentation on the LoginTC REST API may be found at
https://www.logintc.com/docs/rest-api/
"""

import json
import httplib2
import os.path

from logintc import __version__

CA_CERT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'ca_cert.pem')


class LoginTCException(Exception):
    """
    A generic LoginTC client exception.
    """
    pass


class InternalAPIException(LoginTCException):
    """
    Exception caused by internal client exception.
    """

    def __init__(self):
        LoginTCException.__init__(
            self, 'Something went wrong. Please try again.')


class APIException(LoginTCException):
    """
    Exception for failures because of API.
    """

    def __init__(self, code, message):
        LoginTCException.__init__(self, message)

        self.code = code


class NoTokenException(APIException):
    """
    Exception for failure because of no valid token for the specified user and
    domain. This means the token doesn't exist, it's not yet loaded, or it has
    been revoked.
    """

    def __init__(self, code, message):
        APIException.__init__(self, code, message)


class LoginTC(object):
    """
    LoginTC Admin client to manage LoginTC users, domains, tokens and sessions.
    """
    DEFAULT_HOST = 'cloud.logintc.com'
    CONTENT_TYPE = 'application/vnd.logintc.v1+json'
    DEFAULT_ACCEPT_HEADER = 'application/vnd.logintc.v1+json'

    def __init__(self, api_key, host=DEFAULT_HOST, secure=True):
        self.api_key = api_key
        self.host = host
        self.base_uri = 'http%s://%s' % ('s' if secure else '', host)

        if self.host is None:
            self.host = LoginTC.DEFAULT_HOST

        self.http = httplib2.Http(ca_certs=CA_CERT_FILE)
        self.http.follow_all_redirects = True

    def _http(self, method, path, body=None, accept_header=DEFAULT_ACCEPT_HEADER):
        """
        Internal HTTP client for the REST API.
        """
        path = '%s%s' % ('/api', path)

        headers = {'Accept': accept_header,
                   'Authorization': 'LoginTC key="%s"' % self.api_key,
                   'User-Agent': 'LoginTC-Python/%s' % __version__}

        if method in ['PUT', 'POST']:
            if body is not None:
                headers['Content-Type'] = self.CONTENT_TYPE
            else:
                headers['Content-Length'] = '0'

        response, content = self.http.request('%s%s' % (self.base_uri, path),
                                              method,
                                              headers=headers, body=body)

        if str(response['status']) not in ['200', '201', '202']:
            error_json = None

            try:
                error_json = json.loads(content)
            except ValueError:
                raise InternalAPIException

            if 'errors' not in error_json:
                raise InternalAPIException

            errors = error_json['errors']
            error = errors[0]

            code = error['code']
            message = error['message']

            if (code == 'api.error.notfound.token'):
                raise NoTokenException(code, message)

            raise APIException(code, message)

        return content

    def get_user(self, user_id):
        """
        Get user info.

        Returns a dict containing the user's information.
        """
        return json.loads(self._http('GET', '/users/%s' % user_id))

    def create_user(self, username, email, name):
        """
        Create a new user.

        Returns the information for the new user as a dict.
        """
        body = {'username': username, 'email': email, 'name': name}
        return json.loads(self._http('POST', '/users', json.dumps(body)))

    def update_user(self, user_id, email=None, name=None):
        """
        Update a user's name and/or email. Updating the username is not
        permitted.

        Returns the user's previous information as a dict.
        """
        body = {}

        if email is not None:
            body['email'] = email

        if name is not None:
            body['name'] = name

        return json.loads(self._http('PUT', '/users/%s' % user_id,
                                     json.dumps(body)))

    def delete_user(self, user_id):
        """
        Delete a user.

        No return value.
        """
        self._http('DELETE', '/users/%s' % user_id)

    def add_domain_user(self, domain_id, user_id):
        """
        Add a user to a domain.

        No return value.
        """
        self._http('PUT', '/domains/%s/users/%s' % (domain_id, user_id))

    def set_domain_users(self, domain_id, users):
        """
        Set a domain's users.

        The users parameter should be a list of dicts, one dict for each user
        that should be a member in the domain. Each dict should have keys and
        values for username, email, and name.

        If the provided users do not yet exist then they will be created in the
        organization. Existing organization users will be added to the domain.
        The existing domain users that are not present in the users parameter
        will be removed from the domain and their tokens will be revoked.

        No return value.
        """
        self._http('PUT', '/domains/%s/users' % domain_id, json.dumps(users))

    def remove_domain_user(self, domain_id, user_id):
        """
        Remove a user from a domain, revoke their token, and remove any pending
        confirmation codes.

        No return value.
        """
        self._http('DELETE', '/domains/%s/users/%s' % (domain_id, user_id))

    def create_user_token(self, domain_id, user_id):
        """
        Create a user token if one does not exist or if it has been revoked.
        Does nothing if the token is already active or not yet loaded.

        Returns a dict containing the token information.
        """
        return json.loads(self._http('PUT',
                                     '/domains/%s/users/%s/token' % (domain_id, user_id)))

    def get_user_token(self, domain_id, user_id):
        """
        Gets a user's token information.

        Raises a LoginTCException if a token does not exist or has been revoked

        Returns a dict containing the token information.
        """
        return json.loads(self._http('GET',
                                     '/domains/%s/users/%s/token' % (domain_id, user_id)))

    def delete_user_token(self, domain_id, user_id):
        """
        Delete (i.e. revoke) a user's token.

        No return value.
        """
        self._http('DELETE',
                   '/domains/%s/users/%s/token' % (domain_id, user_id))

    def create_session(self, domain_id, user_id=None, attributes=None,
                       username=None, ip_address=None, bypass_code=None, otp=None):
        """
        Create a LoginTC request.

        You must specify either user_id or username. the attributes parameter
        should be a list of dicts, each with keys for 'key' and 'value', and
        may be omitted if not required.

        Returns a dict containing an id and state for the session.
        """
        if attributes is None:
            attributes = []

        body = {'user': {'id': user_id}, 'attributes': attributes}

        if username is not None:
            body = {'user': {'username': username}, 'attributes': attributes}

        if ip_address is not None:
            body['ipAddress'] = ip_address

        if bypass_code is not None:
            body['bypasscode'] = bypass_code
        elif otp is not None:
            body['otp'] = otp

        resp = self._http('POST', '/domains/%s/sessions' % domain_id,
                          json.dumps(body))

        return json.loads(resp)

    def get_session(self, domain_id, session_id):
        """
        Get a session's information.

        Returns a dict containing an id and state for the session.
        """
        resp = self._http('GET', '/domains/%s/sessions/%s' %
                          (domain_id, session_id))

        return json.loads(resp)

    def delete_session(self, domain_id, session_id):
        """
        Delete (i.e. cancel) a session.

        No return value.
        """
        self._http('DELETE',
                   '/domains/%s/sessions/%s' % (domain_id, session_id))

    def get_ping(self):
        """
        Get ping status.

        Returns a dict containing the ping status.
        """
        return json.loads(self._http('GET', '/ping'))

    def get_organization(self):
        """
        Get organization info.

        Returns a dict containing the organization information.
        """
        return json.loads(self._http('GET', '/organization'))

    def get_domain(self, domain_id):
        """
        Get domain info.

        Returns a dict containing the domain's information.
        """
        return json.loads(self._http('GET', '/domains/%s' % domain_id))

    def get_domain_image(self, domain_id):
        """
        Get domain image.

        Returns a byte array containing the domain's image.
        """
        return self._http('GET', '/domains/%s/image' % domain_id, accept_header='image/png')

    def get_domain_user(self, domain_id, user_id):
        """
        Get domain user.

        Returns a dict containing the domain's user with given user_id.
        """
        return json.loads(self._http('GET', '/domains/%s/users/%s' % (domain_id, user_id)))

    def get_domain_users(self, domain_id):
        """
        Get domain users.

        Returns a dict containing an array of domain's users.
        """
        return json.loads(self._http('GET', '/domains/%s/users' % domain_id))


    def get_bypass_code(self, bypass_code_id):
        """
        Get bypass code.

        Returns a dict containing the bypass code's information.
        """
        return json.loads(self._http('GET', '/bypasscodes/%s' % bypass_code_id))

    def get_bypass_codes(self, user_id):
        """
        Get bypass code.

        Returns a dict containing an array of the user's bypass code information.
        """
        return json.loads(self._http('GET', '/users/%s/bypasscodes' % user_id))

    def create_bypass_code(self, user_id, uses_allowed = 1, expiration_time = 0):
        """
        Create a bypass code.

        Returns the information for the bypass code as a dict.
        """
        body = {'usesAllowed': uses_allowed, 'expirationTime': expiration_time}
        return json.loads(self._http('POST', '/users/%s/bypasscodes' % user_id, json.dumps(body)))

    def delete_bypass_code(self, bypass_code_id):
        """
        Delete a bypass code.

        No return value.
        """
        self._http('DELETE', '/bypasscodes/%s' % bypass_code_id)

    def delete_bypass_codes(self, user_id):
        """
        Delete all of user's bypass codes.

        No return value.
        """
        self._http('DELETE', '/users/%s/bypasscodes' % user_id)
    
    def get_hardware_token(self, hardware_token_id):
        """
        Get hardware token.

        Returns a dict containing the hardware tokens's information.
        """
        return json.loads(self._http('GET', '/hardware/%s' % hardware_token_id))

    def get_user_hardware_token(self, user_id):
        """
        Get user hardware token.

        Returns a dict containing the hardware tokens's information.
        """
        return json.loads(self._http('GET', '/users/%s/hardware' % user_id))

    def get_hardware_tokens(self):
        """
        Get hardware token.

        Returns a dict containing an array of the hardware token information.
        """
        return json.loads(self._http('GET', '/hardware'))

    def create_hardware_token(self, alias, serialNumber, type, timeStep, seed):
        """
        Create a hardware token.

        Returns the information for the hardware token as a dict.
        """
        body = {'serialNumber': serialNumber, 'type': type, 'timeStep': timeStep, 'seed': seed}
        
        if alias is not None:
            body['alias'] = alias
        
        return json.loads(self._http('POST', '/hardware', json.dumps(body)))

    def update_hardware_token(self, hardware_token_id, alias=None):
        """
        Update a hardware token's alias.

        Returns the hardware token information as a dict.
        """
        body = {}

        if alias is not None:
            body['alias'] = alias

        return json.loads(self._http('PUT', '/hardware/%s' % hardware_token_id,
                                     json.dumps(body)))

    def delete_hardware_token(self, hardware_token_id):
        """
        Delete a hardware token.

        No return value.
        """
        self._http('DELETE', '/hardware/%s' % hardware_token_id)
        
    def associate_hardware_token(self, user_id, hardware_token_id):
        """
        Associate a hardware token with a user.

        No return value.
        """

        self._http('PUT', '/users/%s/hardware/%s' % (user_id, hardware_token_id))

    def disassociate_hardware_token(self, user_id):
        """
        Disassociate a user's hardware token.

        No return value.
        """
        self._http('DELETE', '/users/%s/hardware' % user_id)
