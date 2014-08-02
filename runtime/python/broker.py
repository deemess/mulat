# coding: utf-8
import os

import ConfigParser
import logging
import subprocess
import zmq
from zmq.eventloop import zmqstream


class Broker(object):
    """
    Main Broker class
    """

    def __init__(self, **kwargs):
        """
        You can pass broker config file path here
        :param kwargs:
        :return:
        """
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

        # default values
        self.config_file = kwargs.get("config") or "broker.conf"

        # init internals
        self.config = ConfigParser.ConfigParser()
        self.logger = logging.getLogger('BROKER')
        self.zmq_context = zmq.Context()
        self.poller = zmq.Poller()
        self.pubs = None
        self.subs = None

        # initialization
        self.load_config()
        self.setup_logging()
        self.logger.info("Loading modules configurations")
        self.load_modules()
        self.logger.info("Running BROKER")
        self.bind()
        # self.logger.info("Installing ioloop")
        # ioloop.install()

        self.run_mainloop()

    def load_config(self):
        """
        Loads broker config
        :return:
        """
        self.config.read(self.config_file)

    def setup_logging(self):
        """
        Sets up broker logging
        :return:
        """
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

    def load_modules(self):
        """
        Loads module's config files and runs modules
        :return:
        """
        modules = self.config.get("main", "modules")
        modules_list = modules.split(",")

        modules_list = [modules_list[0]]  # TODO remove after debug

        self.logger.info("Modules count: {count}".format(
            count=len(modules_list)))

        for module_conf in modules_list:
            config_file_dir = os.path.abspath(module_conf)
            config_file = os.path.join(config_file_dir, "module.conf")
            config = ConfigParser.ConfigParser()
            config.read(config_file)

            module_name = config.get("common", "module")
            module_startcmd = config.get("common", "startcmd")

            pwd = os.path.dirname(config_file)
            subprocess.Popen(module_startcmd.split(" "), cwd=pwd)

    def bind(self):
        """
        Binds broker
        :return:
        """
        self.pubs = self.zmq_context.socket(zmq.PUB)
        self.subs = self.zmq_context.socket(zmq.SUB)

        stream_sub = zmqstream.ZMQStream(self.subs)
        stream_sub.on_recv(self.get_message)

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
        self.subs.connect(sub_conn_string)
        self.subs.setsockopt_string(zmq.SUBSCRIBE, u"")
        # self.subs.setsockopt(zmq.SUBSCRIBE, "9")

    def run_mainloop(self):
        """
        Runs main receive procedure
        :return:
        """
        self.logger.info("Registering sockets")
        self.poller.register(self.subs, zmq.POLLIN)

        self.logger.info("Running mainloop")
        should_continue = True
        while should_continue:
            socks = dict(self.poller.poll())

            if self.subs in socks and socks[self.subs] == zmq.POLLIN:
                message = self.subs.recv()
                print message

    @staticmethod
    def get_message(msg):
        print "Received message: %s" % msg


if __name__ == "__main__":

    broker = Broker()
