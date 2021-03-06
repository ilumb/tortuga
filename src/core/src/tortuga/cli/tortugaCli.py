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

# pylint: disable=no-member,maybe-no-member

import sys
import os
import gettext
import logging
from tortuga.config.configManager import ConfigManager
from tortuga.exceptions.tortugaException import TortugaException
from tortuga.exceptions.invalidArgument import InvalidArgument
from tortuga.exceptions.abstractMethod import AbstractMethod
from optparse import OptionParser
from optparse import OptionGroup
from tortuga.utility.authManager import authorizeRoot
from tortuga.exceptions.userNotAuthorized import UserNotAuthorized


def check_for_root(cls):
    try:
        authorizeRoot()
    except UserNotAuthorized as exc:
        sys.stderr.write(str(exc) + '\n')
        sys.stderr.flush()
        sys.exit(1)

    return cls


# @check_for_root
class TortugaCli(object):
    """
    Base tortuga command line interface class.
    """

    def __init__(self, validArgCount=0):
        self._logger = logging.getLogger(
            'tortuga.cli.%s' % (self.__class__.__name__))
        self._logger.addHandler(logging.NullHandler())

        self._parser = OptionParser(add_help_option=False)
        self._options = None
        self._args = []
        self._validArgCount = validArgCount
        self._username = None
        self._password = None
        self._optionGroupDict = {}
        self._cm = ConfigManager()

        self.__initializeLocale()

        commonGroup = _('Common Tortuga Options')
        self.addOptionGroup(commonGroup, None)

        self.addOptionToGroup(commonGroup, '-h', '--help', action='help',
                              help=_('show this help message and exit'))

        self.addOptionToGroup(commonGroup, '-?', '', action='help',
                              help=_('show this help message and exit'))

        self.addOptionToGroup(commonGroup, '-V', '', action='store_true',
                              dest='cmdVersion', default=False,
                              help=_('print version and exit'))

        self.addOptionToGroup(
            commonGroup, '-d', '--debug', dest='consoleLogLevel',
            help=_('set debug level; valid values are: critical, error,'
                   ' warning, info, debug'))

        self.addOptionToGroup(
            commonGroup, '--username', dest='username',
            help=_('Credential to use when not running as root on the'
                   ' installer.'))

        self.addOptionToGroup(
            commonGroup, '--password', dest='password',
            help=_('Credential to use when not running as root on the'
                   ' installer.'))

    def getLogger(self):
        """ Get logger for this class. """
        return self._logger

    def __initializeLocale(self):
        """Initialize the gettext domain """
        langdomain = 'tortugaStrings'

        # Locate the Internationalization stuff
        localedir = '../share/locale' \
            if os.path.exists('../share/locale') else \
            os.path.join(self._cm.getRoot(), 'share/locale')

        gettext.install(langdomain, localedir)

    def getParser(self):
        """ Get parser for this class. """
        return self._parser

    def addOption(self, *args, **kwargs):
        """ Add option. """
        self._parser.add_option(*args, **kwargs)

    def addOptionToGroup(self, groupName, *args, **kwargs):
        """
        Add option for the given group name.
        Group should be created using addOptionGroup().
        """
        group = self._optionGroupDict.get(groupName)
        group.add_option(*args, **kwargs)

    def addOptionGroup(self, groupName, desc):
        """ Add option group. """
        group = OptionGroup(self._parser, groupName, desc)
        self._parser.add_option_group(group)
        self._optionGroupDict[groupName] = group

    def parseArgs(self, usage=None):
        """
        Parse args

        Raises:
            InvalidArgument
        """

        if usage:
            self._parser.usage = usage

        try:
            self._options, self._args = self._parser.parse_args()
        except SystemExit as rc:
            sys.stdout.flush()
            sys.stderr.flush()
            sys.exit(int(str(rc)))

        if self._validArgCount < len(self._args):
            # Postitional args are not enabled and we have some
            msg = _("Invalid Argument(s):")
            for arg in self._args[self._validArgCount:]:
                msg += " " + arg

            raise InvalidArgument(msg)

        optDict = self._options.__dict__
        if optDict.get('cmdVersion'):
            print(_('{0} version: {1}'.format(
                os.path.basename(sys.argv[0]),
                self._cm.getTortugaRelease())))

            sys.exit(0)

        # Log level.
        consoleLogLevel = optDict.get('consoleLogLevel', None)
        if consoleLogLevel:
            # logManager.setConsoleLogLevel(consoleLogLevel)

            logger = logging.getLogger('tortuga')

            logger.setLevel(logging.DEBUG)

            # create console handler and set level to debug
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)

            # create formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            # add formatter to ch
            ch.setFormatter(formatter)

            # add ch to logger
            logger.addHandler(ch)

        # Promote options to attributes

        self._username = self._options.username
        self._password = self._options.password

        return self._options, self._args

    def usage(self, s=None):
        '''Print the help provided by optparse'''

        if s:
            sys.stderr.write(_('Error: {0}').format(s) + '\n')

        self._parser.print_help()

        sys.exit(1)

    def getOptions(self):
        '''Returns the command line options'''
        return self._options

    def getNArgs(self):
        '''Returns the number of command line arguments'''
        return len(self._args)

    def getArgs(self):
        '''Returns the command line argument list'''
        return self._args

    def getArg(self, i):
        '''Returns the i-th command line argument'''
        return self._args[i]

    def getUsername(self):
        """ Get user name. """
        return self._username

    def getPassword(self):
        """ Get password. """
        return self._password

    def runCommand(self): \
            # pylint: disable=no-self-use
        """ This method must be implemented by the derived class. """

        raise AbstractMethod(
            _('runCommand() has to be overriden in the derived class.'))

    def run(self):
        """
        Invoke runCommand() in derivative class and handle exceptions.
        """
        try:
            self.runCommand()
        except TortugaException as ex:
            print('%s' % (ex.getErrorMessage()))
            raise SystemExit(ex.getErrorCode())
        except SystemExit as ex:
            raise
        except Exception as ex:
            print('%s' % (ex))
            raise SystemExit(-1)

    def getParam(self, xtype, options, oname, config, section, cname,
                 default=None):
        '''
        Get the value of a configurable parameter.
        First look at command line options. Return it if there.
        Then look in the configFile. Return it if there.
        Otherwise return the default.
        '''

        value = self.__getParam2(
            options, oname, config, section, cname, default)

        if xtype == int:
            if not value:
                value = 0
            elif type(value) != int:
                value = int(value)

        elif xtype == bool:
            if type(value) == str:
                value = value.lower() == 'true'
            elif type(value) == int:
                value = bool(value)

        return value

    def __getParam2(self, options, oname, config, section, cname, default): \
            # pylint: disable=no-self-use
        # Command line option takes precedence

        if options and oname in options.__dict__ and \
                options.__dict__[oname] is not None:
            return options.__dict__[oname]

        # Config file is next

        if config and config.has_section(section) and \
                config.has_option(section, cname):
            return config.get(section, cname)

        # Last resort
        return default

    def _parseDiskSize(self, diskSizeParam): \
            # pylint: disable=no-self-use
        """
        Parses diskSizeParam, returns an int value representing
        number of megabytes

        Raises:
            ValueError
        """
        if diskSizeParam.endswith('TB'):
            return int(float(diskSizeParam[:-2]) * 1000000)

        if diskSizeParam.endswith('GB'):
            return int(float(diskSizeParam[:-2]) * 1000)
        elif diskSizeParam.endswith('MB'):
            # Must be an integer
            return int(diskSizeParam[:-2])

        return int(diskSizeParam)

    def _getDiskSizeDisplayStr(self, volSize): \
            # pylint: disable=no-self-use
        if volSize < 1000:
            result = '%s MB' % (volSize)
        elif volSize < 1000000:
            result = '%.3f GB' % (float(volSize) / 1000)
        else:
            result = '%.3f TB' % (float(volSize) / 1000000)

        return result
