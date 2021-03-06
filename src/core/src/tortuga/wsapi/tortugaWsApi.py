# Copyright 2008-2018 Univa Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# pylint: disable=logging-not-lazy

import logging
from urllib.parse import urlparse

from tortuga.web_client import sessionManager
from tortuga.config.configManager import ConfigManager
from tortuga.exceptions.userNotAuthorized import UserNotAuthorized


class TortugaWsApi:
    """
    Base tortuga ws api class.
    """

    def __init__(self, username=None, password=None):
        self._logger = logging.getLogger(
            'tortuga.wsapi.{0}'.format(self.__class__.__name__))
        self._logger.addHandler(logging.NullHandler())

        self._cm = ConfigManager()

        if username is None and password is None:
            self._logger.debug('[%s] Using built-in user credentials' % (
                self.__module__))

            username = self._cm.getCfmUser()
            password = self._cm.getCfmPassword()

        self._username = username
        self._password = password
        self._sm = None

    def _getWsUrl(self, url):
        """Extract scheme and net location from provided url. Use defaults
        if none exist."""

        result = urlparse(url)

        scheme = result.scheme if result.scheme else \
            self._cm.getAdminScheme()

        netloc = result.netloc if result.netloc else \
            '{0}:{1}'.format(self._cm.getInstaller(), self._cm.getAdminPort())

        return '{0}://{1}'.format(scheme, netloc)

    def _getSessionManager(self):
        if not self._sm:
            self._sm = sessionManager.createSession()
        return self._sm

    def getLogger(self):
        """ Get logger for this class. """
        return self._logger

    def getConfigManager(self):
        """ Return configmanager reference """
        return self._cm

    def sendSessionRequest(self, url, method='GET',
                           contentType='application/json', data='',
                           acceptType='application/json'):
        """
        Send authorized session request

        Raises:
            UserNotAuthorized
        """

        sm = self._getSessionManager()

        if not sm.hasSession():
            if self._username is None:
                raise UserNotAuthorized('Username not supplied')

            if self._password is None:
                raise UserNotAuthorized('Password not supplied')

            wsUrl = self._getWsUrl(url)

            # establishSession() sets the 'wsUrl' so the explicit call
            # to setHost() is not required
            sm.establishSession(wsUrl, self._username, self._password)

        return sm.sendRequest(
            url, method, contentType, data, acceptType=acceptType)

    def sendRequest(self, url, method='GET',
                    contentType='application/json', data='',
                    acceptType='application/json'):
        """ Send unauthorized request. """

        sm = self._getSessionManager()

        # Because there's no call to establishSession(), explicitly call
        # setHost()
        sm.setHost(self._getWsUrl(url))

        return self._getSessionManager().sendRequest(
            url, method, contentType, data, acceptType)
