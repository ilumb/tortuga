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

from tortuga.db.dbManager import DbManager
from tortuga.db.tortugaDbApi import TortugaDbApi
from tortuga.exceptions.tortugaException import TortugaException
from tortuga.db import resourceAdaptersDbHandler
from tortuga.objects.resourceAdapter import ResourceAdapter
from tortuga.exceptions.resourceAdapterAlreadyExists \
    import ResourceAdapterAlreadyExists
from tortuga.exceptions.resourceAdapterNotFound \
    import ResourceAdapterNotFound


class ResourceAdapterDbApi(TortugaDbApi):
    def __init__(self):
        TortugaDbApi.__init__(self)

        self._resourceAdaptersDbHandler = resourceAdaptersDbHandler.\
            ResourceAdaptersDbHandler()

    def getResourceAdapter(self, name):
        resourceAdapterObj = None

        try:
            session = DbManager().openSession()

            dbResourceAdapter = self._resourceAdaptersDbHandler.\
                getResourceAdapter(session, name)

            self.loadRelations(dbResourceAdapter, {'kit': True})

            resourceAdapterObj = ResourceAdapter.getFromDbDict(
                dbResourceAdapter.__dict__)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(str(ex))

        return resourceAdapterObj

    def addResourceAdapter(self, name, kitId=None):
        """
        Add resource adapter

        Raises:
            ResourceAdapterAlreadyExists
        """

        resourceAdapterObj = None

        self.getLogger().debug('addResourceAdapter(name=[%s])' % (name))

        try:
            self.getResourceAdapter(name)

            raise ResourceAdapterAlreadyExists(
                'Resource adapter [%s/%s] already exists' % (name, kitId))
        except ResourceAdapterNotFound:
            # Ok, good!
            pass

        try:
            session = DbManager().openSession()

            dbResourceAdapter = self._resourceAdaptersDbHandler.\
                addResourceAdapter(session, name, kitId)

            session.commit()

            resourceAdapterObj = ResourceAdapter.getFromDbDict(
                dbResourceAdapter.__dict__)
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(str(ex))

        # Success!
        self.getLogger().info('Added resource adapter [%s]' % (name))

        return resourceAdapterObj

    def deleteResourceAdapter(self, name):
        """
        Remove resource adapter

        Raises:
        """

        self.getLogger().debug('deleteResourceAdapter(name=[%s])' % (name))

        try:
            session = DbManager().openSession()

            self._resourceAdaptersDbHandler.deleteResourceAdapter(
                session, name)

            session.commit()
        except ResourceAdapterNotFound:
            self.getLogger().info(
                'Resource adapter [%s] not found' % (name))
            return
        except TortugaException:
            raise
        except Exception as ex:
            self.getLogger().exception(str(ex))

        # Success!
        self.getLogger().info('Deleted resource adapter [%s]' % (name))

    def getResourceAdapterList(self):
        resourceAdapters = []

        try:
            session = DbManager().openSession()

            try:
                dbResourceAdapters = self._resourceAdaptersDbHandler.\
                    getResourceAdapterList(session)

                return self.getTortugaObjectList(
                    ResourceAdapter, dbResourceAdapters)
            except TortugaException as ex:
                raise
            except Exception as ex:
                self.getLogger().exception('%s' % ex)
                raise
        finally:
            DbManager().closeSession()

        return resourceAdapters
