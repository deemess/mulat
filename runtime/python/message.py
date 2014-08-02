# coding: utf-8
import base64


class Message(object):
    """
    Messages handler
    """

    TYPE_HEARTBEAT = "beat"
    TYPE_STRING = "string"
    TYPE_BINARY = "binary"
    TYPE_JSON = "json"

    def pack(self, msg_target, msg_type, msg_content=None):
        """
        Packs message into string according to it's type
        :param msg_target: target name
        :param msg_type: message type
        :param msg_content: message content
        :return: packed message string
        """
        if msg_type == self.TYPE_HEARTBEAT:
            return "{0}.heart|{1}".format(msg_target,
                                          self.TYPE_HEARTBEAT)

        if msg_type == self.TYPE_STRING:
            return "{0}|{1}|{2}".format(msg_target,
                                        self.TYPE_STRING,
                                        msg_content.encode("utf8"))

        if msg_type == self.TYPE_BINARY:
            encoded_content = base64.b64encode(msg_content).encode("utf8")
            return "{0}|{1}|{2}".format(msg_target,
                                        self.TYPE_BINARY,
                                        encoded_content)

    def unpack(self, packed_msg):
        """
        Unpacks message into dictionary
        :param packed_msg: packed message string
        :return: message dictionary
        """
        msg_parts = packed_msg.split("|")
        msg_dict = {
            "target": msg_parts[0],
            "type": msg_parts[1],
            "content": None
        }

        # if not heartbeat message
        if len(msg_parts) == 3:
            msg_dict["content"] = msg_parts[2]

        if msg_parts[1] == self.TYPE_BINARY:
            msg_dict["content"] = base64.b64decode(msg_parts[2])

        return msg_dict
