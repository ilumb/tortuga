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

import cherrypy

from tortuga.kit.loader import load_kits
from tortuga.kit.registry import get_all_kit_installers
from .controllers import get_all_ws_controllers, register_ws_controller


def setupRoutes():
    """
    Used to setup RESTFul resources.

    """
    #
    # Ensure all kits are loaded, and their web services are registered
    #
    load_kits()
    for kit_installer_class in get_all_kit_installers():
        kit_installer = kit_installer_class()
        kit_installer.register_web_service_controllers()

    dispatcher = cherrypy.dispatch.RoutesDispatcher()
    dispatcher.mapper.explicit = False
    for controller_class in get_all_ws_controllers():
        controller = controller_class()
        for action in controller.actions:
            dispatcher.connect(
                action['name'],
                action['path'],
                action=action['action'],
                controller=controller,
                conditions=dict(method=action['method'])
            )
    return dispatcher
