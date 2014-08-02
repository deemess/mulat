# coding: utf-8
import unittest
from message import Message

# class TestSequenceFunctions(unittest.TestCase):
#
#     def setUp(self):
#         self.seq = range(10)
#
#     def test_shuffle(self):
#         # make sure the shuffled sequence does not lose any elements
#         random.shuffle(self.seq)
#         self.seq.sort()
#         self.assertEqual(self.seq, range(10))
#
#         # should raise an exception for an immutable sequence
#         self.assertRaises(TypeError, random.shuffle, (1,2,3))
#
#     def test_choice(self):
#         element = random.choice(self.seq)
#         self.assertTrue(element in self.seq)
#
#     def test_sample(self):
#         with self.assertRaises(ValueError):
#             random.sample(self.seq, 20)
#         for element in random.sample(self.seq, 5):
#             self.assertTrue(element in self.seq)
#
# if __name__ == '__main__':
#     unittest.main()


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
