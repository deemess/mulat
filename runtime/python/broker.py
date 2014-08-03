# coding: utf-8
import os
import time
import threading

import ConfigParser
import logging
import subprocess
import zmq
from zmq.eventloop import zmqstream

from message import Message


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
        self.modules_list = []
        # self.modules_process_list = []
        self.modules_process_dict = {}
        self.message = Message()

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
        self.logger.info("Running modules")
        self.run_modules()
        self.logger.info("Running BROKER")
        self.bind()
        # self.logger.info("Installing ioloop")
        # ioloop.install()

        # self.run_mainloop()
        self.mainloop_thread()

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
        self.modules_list = modules.split(",")

        # self.modules_list = [self.modules_list[0]]  # TODO remove after debug
        self.logger.info(self.modules_list)

        self.logger.info("Modules count: {count}".format(
            count=len(self.modules_list)))

    def run_modules(self):
        for module_conf in self.modules_list:
            config_file_dir = os.path.abspath(
                os.path.normpath(module_conf.strip()))
            config_file = os.path.join(config_file_dir, "module.conf")
            self.logger.info("Loading '{0}'".format(config_file))
            config = ConfigParser.ConfigParser()
            config.read(config_file)

            module_name = config.get("common", "module")
            module_startcmd = config.get("common", "startcmd")

            pwd = os.path.dirname(config_file)
            process_cmd = module_startcmd.split(" ")
            self.logger.debug("Module run command: '{0}'".format(process_cmd))
            process = subprocess.Popen(process_cmd, cwd=pwd)

            # self.modules_process_list.append(process)

            self.modules_process_dict[module_name] = {
                "name": module_name,
                "process": process
            }

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
        self.subs.bind(sub_conn_string)
        self.subs.setsockopt_string(zmq.SUBSCRIBE, u"")

    def run_mainloop(self):
        """
        Runs main receive procedure
        :return:
        """
        self.logger.info("Registering broker sockets")
        self.poller.register(self.subs, zmq.POLLIN)

        self.logger.info("Running mainloop")
        should_continue = True
        while should_continue:
            socks = dict(self.poller.poll())

            if self.subs in socks and socks[self.subs] == zmq.POLLIN:
                message = self.subs.recv()
                self.logger.debug("Broker received '{0}'".format(message))
                time.sleep(1)

                packed_msg = self.message.pack("module1.in.slot1",
                                  Message.TYPE_STRING,
                                  message + " RETRANSLATED")

                self.pubs.send(packed_msg)

    def mainloop_thread(self):
        thread = threading.Thread(target=self.run_mainloop)
        thread.start()
        thread.join()

    @staticmethod
    def get_message(msg):
        print "Received message: %s" % msg


if __name__ == "__main__":

    broker = Broker()
