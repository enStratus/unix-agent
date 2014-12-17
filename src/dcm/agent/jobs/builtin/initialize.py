#  ========= CONFIDENTIAL =========
#
#  Copyright (C) 2010-2014 Dell, Inc. - ALL RIGHTS RESERVED
#
#  ======================================================================
#   NOTICE: All information contained herein is, and remains the property
#   of Dell, Inc. The intellectual and technical concepts contained herein
#   are proprietary to Dell, Inc. and may be covered by U.S. and Foreign
#   Patents, patents in process, and are protected by trade secret or
#   copyright law. Dissemination of this information or reproduction of
#   this material is strictly forbidden unless prior written permission
#   is obtained from Dell, Inc.
#  ======================================================================

import logging
from dcm.agent import utils
from dcm.agent.jobs.builtin.add_user import AddUser
from dcm.agent.jobs.builtin.make_temp import MakeTemp
from dcm.agent.jobs.builtin.rename import Rename

import dcm.agent.jobs as jobs


_g_logger = logging.getLogger(__name__)


class InitializeJob(jobs.Plugin):

    protocol_arguments = {
        "cloudId":
        ("The cloud ID on which this agent is running.",
         True, str, None),
        "customerId":
        ("The ID of the customer running this server.  A new user will be "
         "created with the name c<customerId>.",
         True, long, None),
        "regionId":
        ("Sets the default region that will be used by this agent in "
         "future cloud related operations",
         True, str, None),
        "zoneId":
        ("The default zone that will be used by this agent in future "
         "cloud operations.", True, str, None),
        "serverId":
        ("A unique ID for this server.  This will be used in future "
         "communication with the agent manager as a means of "
         "authentication.",
         True, str, None),
        "serverName":
        ("The name of this server. The hostname will be set to this value.",
         True, str, None),
        "encryptedEphemeralFsKey":
        ("The file system key for encrypted ephemeral file systems.",
         True, utils.base64type_convertor, None)
    }

    def __init__(self, conf, job_id, items_map, name, arguments):
        super(InitializeJob, self).__init__(
            conf, job_id, items_map, name, arguments)

        self.rename = Rename(self.conf, self.job_id, {"script_name": "rename"},
                             "rename",
                             {"serverName": self.arguments["serverName"]})
        self.add_user = AddUser(self.conf, self.job_id,
                                {"script_name": "addUser"}, "add_user",
                                {"firstName": "Customer",
                                 "lastName": "Account",
                                 "password": None,
                                 "authentication": None,
                                 "administrator": "false",
                                 "userId": utils.make_id_string(
                                     "c", self.args.customerId)})

    def run(self):
        utils.log_to_dcm(logging.DEBUG, "Initialize run")
        # verify that the parameters in initialize match what came in on the
        # connection
        try:
            utils.log_to_dcm(logging.INFO,
                             "Renaming the host to %s" % self.args.serverName)
            res_doc = self.rename.run()
            if res_doc["return_code"] != 0:
                res_doc["message"] = res_doc["message"] + " : rename failed"
                return res_doc

            # make the temp directory
            utils.log_to_dcm(logging.INFO, "Create the temporary directory")
            # add customer user
            utils.log_to_dcm(logging.INFO, "Adding the user")
            res_doc = self.add_user.run()
            if res_doc["return_code"] != 0:
                res_doc["message"] = res_doc["message"] + " : addUser failed"
                return res_doc

            self.conf.state = "RUNNING"
            return {"return_code": 0, "message": "",
                    "error_message": "", "reply_type": "void"}
        except Exception as ex:
            _g_logger.exception("initialize faild: " + str(ex))
            return {'return_code': 1, "message": ex.message}


def load_plugin(conf, job_id, items_map, name, arguments):
    _g_logger.debug("loading %s" % __name__)
    return InitializeJob(conf, job_id, items_map, name, arguments)
