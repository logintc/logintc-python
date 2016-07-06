"""
The LoginTC Python client is a complete LoginTC REST API client to manage
LoginTC organizations, users, domains, tokens and to create login sessions.
"""

__version_info__ = ('1', '1', '7')
__version__ = '.'.join(__version_info__)

from logintc.client import LoginTC
from logintc.client import LoginTCException
from logintc.client import InternalAPIException
from logintc.client import APIException
from logintc.client import NoTokenException
