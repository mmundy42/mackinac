from __future__ import absolute_import
import requests
import configparser
import json
from os import environ, path
from getpass import getpass
import base64
import six


def get_token(username, password=None, token_type='patric', timeout=5):
    """ Get an authentication token for SEED web services.

        The authentication token is also stored in the .patric_config file in
        the user's home directory. The SeedClient object retrieves the
        authentication token from the file so the user does not need to keep
        getting a new token.

    Parameters
    ----------
    username : str
        User name
    password : str, optional
        Password or None to prompt and enter password
    token_type : {'patric', 'rast'}, optional
        Type of authentication token
    timeout : integer
        Number of seconds to wait for response

    Returns
    -------
    str
        User ID (which can be different than user name)
    """

    # Prompt for a password if not specified.
    if password is None:
        password = getpass(prompt='{0} password: '.format(token_type))

    # Get an authentication token from the specified web service.
    if token_type == 'patric':
        url = 'https://user.patricbrc.org/authenticate'
        request_data = {'username': username, 'password': password}
        response = requests.post(url, data=request_data, timeout=timeout)
        if response.status_code != requests.codes.OK:
            response.raise_for_status()
        token = response.text
        user_id = token.split('|')[0].replace('un=', '')

    elif token_type == 'rast':
        url = 'http://rast.nmpdr.org/goauth/token?grant_type=client_credentials&client_id={0}'.format(username)
        headers = dict()
        headers['Content-Type'] = 'application/json'
        headers['Authorization'] = 'Basic {0}'\
            .format(base64.urlsafe_b64encode(six.b(username + ':' + password)).decode("ascii"))
        response = requests.get(url, headers=headers, timeout=timeout)
        if response.status_code != requests.codes.OK:
            response.raise_for_status()
        data = json.loads(response.text)
        token = data['access_token']
        user_id = data['client_id']

    else:
        raise ValueError('Token token_type {0} is not valid'.format(token_type))

    # Save the authentication data in config file.
    config_file = path.join(environ['HOME'], '.patric_config')
    config = configparser.ConfigParser()
    config.read(config_file)
    if not config.has_section('authentication'):
        config.add_section('authentication')
    config.set('authentication', 'token', token)
    config.set('authentication', 'user_id', user_id)
    config.write(open(config_file, 'w'))

    return user_id


class ServerError(Exception):
    """ Exception raised when server returns an error. """

    def __init__(self, message, name='JSONRPCError', code=-32603, data=None, error=None):
        # The name is always 'JSONRPCError and the code is always -32603 because it
        # is hard-coded in the server.
        self.name = name
        self.code = code

        if message is None:
            self.data = data or error or ''
            self.message = self.data
        else:
            # Separate the lines in the message and store as an array of lines.
            self.data = message.split('\n')

            # If the first line has the _ERROR_ delimiter, extract the message.
            if self.data[0].startswith('_ERROR_'):
                self.message = self.data[0][7:-7]

            # If the second line has the _ERROR_ delimiter, extract the message.
            if self.data[0] == 'JSONRPC error:' and len(self.data) > 1 and self.data[1].startswith('_ERROR_'):
                self.message = self.data[1][7:-7]

            # Otherwise, use the first line as the message.
            else:
                self.message = self.data[0]

    def traceback(self):
        output = ''
        for line in self.data:
            output += line + '\n'
        return output

    def __str__(self):
        return self.message


class ObjectNotFoundError(Exception):
    """ Exception raised when an object cannot be retrieved from workspace. """

    def __init__(self, message, data):
        self.message = message
        self.data = data

    def traceback(self):
        output = ''
        for line in self.data:
            output += line + '\n'
        return output

    def __str__(self):
        return self.message


class ObjectTypeError(Exception):
    """ Exception raised when an object is the wrong type for the operation. """

    def __init__(self, message, data):
        self.message = message
        self.data = data

    def traceback(self):
        output = ''
        for line in self.data:
            output += line + '\n'
        return output

    def __str__(self):
        return self.message


class DuplicateGapfillError(Exception):
    """ Exception raised when a gap fill solution is already available. """
    pass


class JobError(Exception):
    """ Exception raised when a job submitted to app service ended in error. """
    pass


class AuthenticationError(Exception):
    """ Exception raised when there is a problem with authentication token. """


def handle_server_error(e, references=None):
    """ Handle an error returned by a PATRIC service server.

    Parameters
    ----------
    e : Exception
        Exception returned by server
    references : list
        List of workspace references in input parameters of server method

    Raises
    -------
    ObjectNotFoundError
        When server method had a problem with a workspace reference
    DuplicateGapfillError
        When a gap fill solution already exists for a media condition
    ObjectTypeError
        When a workspace reference refers to an object of the wrong type
    Exception
        Source exception for all other cases
    """

    # Map a generic server error to a specific exception.
    if isinstance(e, ServerError):
        # Errors returned by ModelSEED server do not indicate which workspace reference had
        # a problem. One of the references in the list is the one that caused the problem.
        reference_string = ''
        if references is not None:
            reference_string = '"{0}"'.format('" or "'.join(references))
        if 'Object not found!' in e.message or 'Owner not specified in deletion!' in e.message:
            msg = 'An object was not found in workspace: {0}'.format(reference_string)
            raise ObjectNotFoundError(msg, e.data)

        if 'does not include at least a top level directory!' in e.message:
            msg = 'An object reference is missing a top level directory: {0}'.format(reference_string)
            raise ObjectNotFoundError(msg, e.data)

        if 'Path does not point to folder or object:' in e.message:
            msg = 'An object was not found in workspace: {0}'.format(reference_string)
            raise ObjectNotFoundError(msg, e.data)

        if 'User lacks permission to / for requested action!' in e.message:
            msg = 'User does not have permission to a directory in an object reference: {0}'.format(reference_string)
            raise ObjectNotFoundError(msg, e.data)

        if 'is not a valid object path!' in e.message:
            msg = 'An object reference is not a valid path: {0}'.format(reference_string)
            raise ObjectNotFoundError(msg, e.data)

        if 'No gap filling needed on specified condition' in e.message:
            raise DuplicateGapfillError('Gap fill solution already available for specified media')

        if 'does not match specified type' in e.message:
            raise ObjectTypeError(e.message, e.data)

    # Raise the exception again.
    raise e


class SeedClient(object):
    """ Client for SEED web services """

    def __init__(self, url, name, token=None):
        """ Initialize object.

        Parameters
        ----------
        url : str
            URL of service endpoint
        name : str
            Name of service
        token : str, optional
            Authentication token for SEED web services, when None get the
            token from the .patric_config file when calling a method
        """

        self.url = url
        self.name = name
        self.username = None
        if token is not None:
            self.username = token.split('|')[0].replace('un=', '')

        # Create the headers for the request to the server.
        self.headers = dict()
        self.headers['AUTHORIZATION'] = token

        return

    def call(self, method, params, timeout=1800):
        """ Call a server method and wait for the response.

        Parameters
        ----------
        method: str
            Name of server method
        params : dict
            Dictionary of input parameters for method
        timeout : integer
            Number of seconds to wait for response

        Returns
        -------
        data
            Output of method in JSON format

        Raises
        ------
        ServerError
            When server returns an error response
        """

        # If needed, look for the authentication token in the Patric config file.
        if self.headers['AUTHORIZATION'] is None:
            self.set_authentication_token()

        # Create the body of the request for the specified method.
        request_data = dict()
        request_data['method'] = self.name + '.' + method
        request_data['params'] = params
        request_data['version'] = '1.1'
        request_data['id'] = '1'

        # Send the request to the server and get back a response.
        response = requests.post(self.url, data=json.dumps(request_data), headers=self.headers, timeout=timeout)

        if response.status_code == requests.codes.server_error:
            if 'content-type' in response.headers and response.headers['content-type'] == 'application/json':
                err = json.loads(response.text)
                if 'error' in err:
                    raise ServerError(**err['error'])
                else:
                    raise ServerError(response.text)
            else:
                raise ServerError(response.text)

        if response.status_code != requests.codes.OK:
            response.raise_for_status()
        return json.loads(response.text)['result'][0]  # Get the output from the method in the response

    def set_authentication_token(self):
        """ Set the authentication token from the config file.

        Raises
        ------
        AuthenticationError
            When there is a problem with the authentication section in the config file
        """

        config = configparser.ConfigParser()
        config.read(path.join(environ['HOME'], '.patric_config'))
        try:
            self.headers['AUTHORIZATION'] = config.get('authentication', 'token')
            self.username = config.get('authentication', 'user_id')
        except (configparser.NoSectionError, configparser.NoOptionError):
            self.headers['AUTHORIZATION'] = None
            raise AuthenticationError('Call get_token() to obtain an authentication token')
