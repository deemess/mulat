# coding: utf-8

import ConfigParser
import logging
import zmq
from zmq.eventloop import ioloop, zmqstream


class Broker(object):
    """

    """

    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

        # default values
        self.config_file = kwargs.get("config") or "broker.conf"

        # init internals
        self.config = ConfigParser.ConfigParser()
        self.logger = logging.getLogger('BROKER')
        self.zmq_context = zmq.Context()
        self.pubs = None
        self.subs = None

        # initialization
        self.load_config()
        self.setup_logging()
        self.logger.info("Running BROKER")
        self.bind()
        self.logger.info("Installing ioloop")
        ioloop.install()

        self.run_mainloop()

    def load_config(self):
        self.config.read(self.config_file)

    def setup_logging(self):
        # TODO: make option for formatting
        formatter = logging.Formatter(
            "%(asctime)s|%(name)s|%(levelname)s| %(message)s")
        log_filename = self.config.get("log", "logFile")
        file_log = logging.FileHandler(log_filename)
        file_log.setFormatter(formatter)
        self.logger.addHandler(file_log)
        # TODO: make option for logging level
        self.logger.setLevel(logging.DEBUG)

        if self.config.getboolean("log", "logToStdout"):
            stream_log = logging.StreamHandler()
            stream_log.setFormatter(formatter)
            self.logger.addHandler(stream_log)

    def bind(self):
        self.pubs = self.zmq_context.socket(zmq.PUB)
        self.subs = self.zmq_context.socket(zmq.SUB)

        address = self.config.get("main", "listen")
        pub_port = self.config.get("main", "pubPort")
        sub_port = self.config.get("main", "subPort")
        pub_conn_string = "tcp://{address}:{port}".format(address=address,
                                                          port=pub_port)
        sub_conn_string = "tcp://{address}:{port}".format(address=address,
                                                          port=sub_port)

        self.logger.info("Binding PUB on '{0}'".format(pub_conn_string))
        self.pubs.bind(pub_conn_string)
        self.logger.info("Binding SUB on '{0}'".format(sub_conn_string))
        self.subs.bind(sub_conn_string)
        self.subs.setsockopt_string(zmq.SUBSCRIBE, "".decode("utf8"))

    def run_mainloop(self):
        self.logger.info("Running mainloop")
        ioloop.IOLoop.instance().start()


# def main():


    # context = zmq.Context()
    # pubs = context.socket(zmq.PUB)
    # pubs.bind("tcp://*:7570")
    # subs = context.socket(zmq.SUB)
    # subs.bind("tcp://*:7770")
    # subs.setsockopt_string(zmq.SUBSCRIBE, "".decode("ascii"))
    
    # while True:
    #     message = subs.recv_string()
    #     print message
    #     pubs.send_string(message)

    # while True:
    #     pass

if __name__ == "__main__":
    broker = Broker()
