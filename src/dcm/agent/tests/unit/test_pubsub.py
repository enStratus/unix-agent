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
import unittest
import uuid

import dcm.agent.events.callback as events
import dcm.agent.events.pubsub as pubsub
import dcm.agent.tests.utils.general as test_utils


class TestPubSub(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        test_utils.connect_to_debugger()

    def setUp(self):
        self._event_space = events.EventSpace()
        self._pub_sub = pubsub.PubSubEvent(self._event_space)

    def test_simple_publish(self):
        topic = str(uuid.uuid4())
        x_val = 1
        y_val = []
        apple_val = "sauce"

        def test_callback(x_param, y_param, apple_param=None):
            self.assertEqual(x_param, x_val)
            self.assertEqual(y_param, y_val)
            self.assertEqual(apple_param, apple_val)
            y_val.append("called")

        self._pub_sub.subscribe(topic, test_callback)
        self._pub_sub.publish(topic,
                              topic_args=(x_val, y_val),
                              topic_kwargs={'apple_param': apple_val})

        self._event_space.poll(timeblock=0.0)
        self.assertEqual(len(y_val), 1)

    def test_multiple_subscribe(self):
        topic = str(uuid.uuid4())
        x_val = []

        def test_callback1(x_param):
            x_param.append(1)

        def test_callback2(x_param):
            x_param.append(2)

        def test_callback3(x_param):
            x_param.append(3)

        self._pub_sub.subscribe(topic, test_callback1)
        self._pub_sub.subscribe(topic, test_callback2)
        self._pub_sub.subscribe(topic, test_callback3)
        self._pub_sub.publish(topic, topic_args=(x_val,))

        self._event_space.poll(timeblock=0.0)
        self.assertEqual(len(x_val), 3)
        self.assertIn(1, x_val)
        self.assertIn(2, x_val)
        self.assertIn(3, x_val)

    def test_public_empty(self):
        topic = str(uuid.uuid4())
        self._pub_sub.publish(topic)
        self._event_space.poll(timeblock=0.0)

    def test_unsubscribe(self):
        topic = str(uuid.uuid4())

        def test_callback():
            pass

        self._pub_sub.subscribe(topic, test_callback)
        self._pub_sub.unsubscribe(topic, test_callback)
        try:
            self._pub_sub.unsubscribe(topic, test_callback)
            passes = False
        except KeyError:
            passes = True
        self.assertTrue(passes)

    def test_done_callback(self):
        topic = str(uuid.uuid4())
        x_val = []

        def test_callback1(x_param):
            x_param.append(1)

        def test_callback2(x_param):
            x_param.append(2)

        def test_callback3(x_param):
            x_param.append(3)

        def done_cb(topic_error, x_param=None):
            self.assertEqual(len(x_param), 3)
            self.assertIn(1, x_param)
            self.assertIn(2, x_param)
            self.assertIn(3, x_param)
            self.assertIsNone(topic_error)
            x_param.append("done")

        self._pub_sub.subscribe(topic, test_callback1)
        self._pub_sub.subscribe(topic, test_callback2)
        self._pub_sub.subscribe(topic, test_callback3)
        self._pub_sub.publish(topic,
                              topic_args=(x_val,),
                              done_cb=done_cb,
                              done_kwargs={'x_param': x_val})

        self._event_space.poll(timeblock=0.0)
        self.assertIn('done', x_val)

    def test_done_error_callback(self):
        topic = str(uuid.uuid4())
        x_val = []

        def test_callback1(x_param):
            x_param.append(1)

        def test_callback2(x_param):
            raise Exception("error")

        def test_callback3(x_param):
            x_param.append(3)

        def done_cb(topic_error, x_param=None):
            self.assertLess(len(x_param), 3)
            self.assertIsNotNone(topic_error)
            x_param.append("done")

        self._pub_sub.subscribe(topic, test_callback1)
        self._pub_sub.subscribe(topic, test_callback2)
        self._pub_sub.subscribe(topic, test_callback3)
        self._pub_sub.publish(topic,
                              topic_args=(x_val,),
                              done_cb=done_cb,
                              done_kwargs={'x_param': x_val})

        self._event_space.poll(timeblock=0.0)
        self.assertIn('done', x_val)
