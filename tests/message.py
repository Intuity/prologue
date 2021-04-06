# Copyright 2020, Peter Birch, mailto:peter@lightlogic.co.uk
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from random import choice, randint
from unittest.mock import MagicMock, call

import pytest

from prologue.common import PrologueError
from prologue.directives.message import Message

from .common import random_str

INFO_TAGS    = ["info"]
WARNING_TAGS = ["warn", "warning", "todo", "fixme"]
ERROR_TAGS   = ["error", "danger", "fatal"]

def test_message_types():
    """ Create different level messages and check they print on evaluation """
    for m_class, m_tags in [
        ("INFO", INFO_TAGS), ("WARNING", WARNING_TAGS), ("ERROR", ERROR_TAGS),
    ]:
        for tag in m_tags:
            msg = Message.directive(None)
            # Sanity check initial state
            assert msg.msg_class == None
            assert msg.msg_text  == None
            # Invoke with the tag and a random message
            msg_str = random_str(30, 50, spaces=True)
            msg.invoke(tag, msg_str)
            assert msg.msg_class == m_class
            assert msg.msg_text  == msg_str
            # Test that the message is printed out OK
            ctx = MagicMock()
            msg.evaluate(ctx)
            if m_class == "INFO":
                ctx.pro.info_message.assert_has_calls([call(msg_str, source=(None, 0))])
            elif m_class == "WARN":
                ctx.pro.warning_message.assert_has_calls([call(msg_str, source=(None, 0))])
            elif m_class == "ERROR":
                ctx.pro.error_message.assert_has_calls([call(msg_str, source=(None, 0))])

def test_message_bad_tags():
    """ Check that a message cannot be invoked with a bad type """
    for _x in range(100):
        msg = Message.directive(None)
        # Sanity check initial state
        assert msg.msg_class == None
        assert msg.msg_text  == None
        # Invoke with a fake tag
        bad_tag = random_str(4, 10, avoid=[*INFO_TAGS, *WARNING_TAGS, *ERROR_TAGS])
        with pytest.raises(PrologueError) as excinfo:
            msg.invoke(bad_tag, random_str(30, 50, spaces=True))
        assert f"Unrecognised message type {bad_tag}" in str(excinfo.value)
