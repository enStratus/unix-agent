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
import os

from dcm.agent import cloudmetadata, jobs
import dcm.agent


FOR_TEST_AGENT_ID_ENV = "FOR_TEST_AGENT_ID_ENV"

_g_logger = logging.getLogger(__name__)


def get_handshake(conf):
    plugin_dict = jobs.get_all_plugins(conf)
    features = conf.features.copy()
    for plugin_name in plugin_dict:
        p_feature = jobs.get_module_features(
            conf, plugin_name, plugin_dict[plugin_name])
        features.update(p_feature)

    features['plugins'] = get_plugin_handshake_descriptor(conf)

    if conf.test_skip_handshake:
        # TODO make this configurable from the test conf files
        return {
            'ipv4': ["127.0.0.1"],
            'ipv6': [],
            'agent_id': "test-agent",
            'vm_instance': "vdeadbeef",
            'injected_id': "ideadbeef",
            'token': 'tdeadbeef',
            'version': dcm.agent.g_version,
            'protocol_version': dcm.agent.g_protocol_version,
            'platform': conf.platform_name,
            'features': features
        }

    ipv4s = conf.meta_data_object.get_handshake_ip_address(conf)
    ipv6s = []
    injected_id = cloudmetadata.get_env_injected_id()
    if not injected_id:
        _g_logger.debug("No ENV ID set, check the cloud specific "
                        "metadata object")
        injected_id = conf.meta_data_object.get_injected_id()
    agent_id = conf.agent_id
    if FOR_TEST_AGENT_ID_ENV in os.environ:
        agent_id = os.environ[FOR_TEST_AGENT_ID_ENV]

    vm_instance = conf.meta_data_object.get_instance_id()

    handshake_doc = {
        'ipv4': ipv4s,
        'ipv6': ipv6s,
        'agent_id': agent_id,
        'token': conf.token,
        'vm_instance': vm_instance,
        'injected_id': injected_id,
        'version': dcm.agent.g_version,
        'protocol_version': dcm.agent.g_protocol_version,
        'platform': conf.platform_name,
        'platform_version': conf.platform_version,
        'features': features
    }
    return handshake_doc


def get_plugin_handshake_descriptor(conf):
    items = jobs.get_all_plugins(conf)
    command_name_list = [i for i in items]
    return command_name_list
