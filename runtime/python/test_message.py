# coding: utf-8
import unittest
from message import Message


class TestMessage(unittest.TestCase):

    def setUp(self):
        self.message = Message()

    def test_pack_heartbeat(self):
        packed_msg = self.message.pack("test1",
                                       Message.TYPE_HEARTBEAT)

        self.assertEqual(packed_msg, "test1.heart|beat")

    def test_pack_string(self):
        packed_msg = self.message.pack("test1.slot",
                                       Message.TYPE_STRING,
                                       "message string")

        self.assertEqual(packed_msg, "test1.slot|string|message string")

    def test_pack_binary(self):
        packed_msg = self.message.pack("test1.slot",
                                       Message.TYPE_BINARY,
                                       "message string")

        self.assertEqual(packed_msg, "test1.slot|binary|bWVzc2FnZSBzdHJpbmc=")
