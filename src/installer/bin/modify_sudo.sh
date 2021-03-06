#!/bin/sh

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


[ -d /etc/sudoers.d ] || {
    sudodir=/etc/sudoers.d

    echo "Creating $sudodir directory"

    mkdir $sudodir

    if ! `grep --quiet "^#includedir /etc/sudoers.d$" /etc/sudoers`; then
        echo "#includedir /etc/sudoers.d" >>/etc/sudoers
    fi
}

( rm -f /etc/sudoers.d/tortuga; umask 0227; cat >/etc/sudoers.d/tortuga <<ENDL
# TODO: this must be fixed to only disable 'requiretty' for the Tortuga
# users.

Defaults !requiretty

apache ALL=(ALL) NOPASSWD: /opt/tortuga/bin/run_cluster_update.sh
apache ALL=(ALL) NOPASSWD: /opt/tortuga/bin/pre-add-host
puppet ALL=(ALL) NOPASSWD: /opt/tortuga/bin/get-tortuga-node
puppet ALL=(ALL) NOPASSWD: /opt/tortuga/bin/get-provisioning-networks
puppet ALL=(ALL) NOPASSWD: /opt/tortuga/bin/get-component-node-list
puppet ALL=(ALL) NOPASSWD: /opt/tortuga/bin/get-nodes-with-component
puppet ALL=(ALL) NOPASSWD: /opt/tortuga/bin/get-provisioning-nics
ENDL
)

# Validate sudo file
visudo -c
