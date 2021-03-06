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

# pylint: disable=not-callable,multiple-statements,no-member

from sqlalchemy import or_, and_
from sqlalchemy.orm.exc import NoResultFound

from tortuga.db.tortugaDbObjectHandler import TortugaDbObjectHandler
from tortuga.db.hardwareProfiles import HardwareProfiles
from tortuga.exceptions.hardwareProfileNotFound \
    import HardwareProfileNotFound
from tortuga.db import networksDbHandler
from tortuga.db import networkDevicesDbHandler
from tortuga.exceptions.softwareProfileNotIdle \
    import SoftwareProfileNotIdle
from tortuga.exceptions.invalidArgument import InvalidArgument


class HardwareProfilesDbHandler(TortugaDbObjectHandler):
    """
    This class handles hardwareProfiles table.
    """

    def __init__(self):
        TortugaDbObjectHandler.__init__(self)

        self._networksDbHandler = networksDbHandler.NetworksDbHandler()
        self._networkDevicesDbHandler = networkDevicesDbHandler.\
            NetworkDevicesDbHandler()

    def getHardwareProfile(self, session, name):
        """
        Return hardwareProfile.
        """

        self.getLogger().debug('Retrieving hardware profile [%s]' % (name))

        try:
            return session.query(HardwareProfiles).filter(
                HardwareProfiles.name == name).one()
        except NoResultFound:
            raise HardwareProfileNotFound(
                'Hardware profile [%s] not found.' % (name))

    def getHardwareProfileById(self, session, _id):
        """
        Return hardwareProfile.
        """

        self.getLogger().debug(
            'Retrieving hardware profile ID [%s]' % (_id))

        dbHardwareProfile = session.query(HardwareProfiles).get(_id)

        if not dbHardwareProfile:
            raise HardwareProfileNotFound(
                'Hardware profile ID [%s] not found.' % (_id))

        return dbHardwareProfile

    def getHardwareProfileList(self, session, tags=None):
        """
        Get list of hardwareProfiles from the db.
        """

        self.getLogger().debug('Retrieving hardware profile list')

        searchspec = []

        # Build searchspec from specified tags
        for tag in tags or []:
            if len(tag) == 2:
                searchspec.append(
                    and_(HardwareProfiles.tags.any(name=tag[0]),
                         HardwareProfiles.tags.any(value=tag[1])))
            else:
                searchspec.append(HardwareProfiles.tags.any(name=tag[0]))

        return session.query(HardwareProfiles).filter(
            or_(*searchspec)).order_by(HardwareProfiles.name).all()

    def setIdleSoftwareProfile(self, dbHardwareProfile,
                               dbSoftwareProfile=None): \
            # pylint: disable=no-self-use
        if dbSoftwareProfile and not dbSoftwareProfile.isIdle:
            # Don't allow a non-idle software profile to be used as an
            # idle profile

            raise SoftwareProfileNotIdle(
                'Software profile [%s] not an idle profile' % (
                    dbSoftwareProfile.name))

        if not dbHardwareProfile:
            raise InvalidArgument('Hardware profile must not be None')

        dbHardwareProfile.idlesoftwareprofile = dbSoftwareProfile
