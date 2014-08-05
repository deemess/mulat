# coding: utf-8
import ConfigParser
import logging


class LoggingManager(object):
    """
    Manages logging, uses [log] section of config file and 'debug'
    option of [main]

    todo: probably, it's singletone
    """

    def __init__(self, config_file="broker.conf"):
        self.config = ConfigParser.ConfigParser()
        self.config.read(config_file)

        # todo: move to config
        self.log_format = "%(asctime)s|%(name)s|%(levelname)s| %(message)s"

    def setup_logger(self, name):
        logger = logging.getLogger(name)
        formatter = logging.Formatter(self.log_format)

        log_filename = self.config.get("log", "logFile")

        file_log = logging.FileHandler(log_filename)
        file_log.setFormatter(formatter)
        logger.addHandler(file_log)
        logger.setLevel(logging.ERROR)

        if self.config.getboolean("main", "debug"):
            logger.setLevel(logging.DEBUG)

        if self.config.getboolean("log", "logToStdout"):
            stream_log = logging.StreamHandler()
            stream_log.setFormatter(formatter)
            logger.addHandler(stream_log)

        return logger
