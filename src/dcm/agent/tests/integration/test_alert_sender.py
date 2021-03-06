#
#  Copyright (C) 2014 Dell, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import getpass
import os
import shutil
import tempfile
import unittest

from dcm.agent import logger

import dcm.agent.cmd.configure as configure
import dcm.agent.tests.utils.general as test_utils


class TestAlertSender(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.run_as_user = getpass.getuser()
        test_utils.connect_to_debugger()
        cls.test_base_path = tempfile.mkdtemp()
        cls.test_conf_path = os.path.join(
            cls.test_base_path, "etc", "agent.conf")
        conf_args = ["-c", "Other",
                     "-u", "http://doesntmatter.org/ws",
                     "-p", cls.test_base_path,
                     "-t", os.path.join(cls.test_base_path, "tmp"),
                     "-C", "ws",
                     "-U", cls.run_as_user,
                     "-l", "/tmp/agent_status_test.log",
                     "--intrusion-detection-ossec", "true",
                     "--install-extras",
                     "--extra-package-location", os.environ['DCM_AGENT_TEST_EXTRA_PACKAGE_URL']]
        rc = configure.main(conf_args)
        if rc != 0:
            raise Exception("We could not configure the test env")

    @classmethod
    def tearDownClass(cls):
        logger.clear_dcm_logging()
        shutil.rmtree(cls.test_base_path)

    def tearDown(self):
        os.system("rm -r /opt/dcm-agent-extras")
        os.system("dpkg --purge dcm-agent-extras")
        os.system("pkill -9 ossec")
