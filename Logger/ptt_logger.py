import logging


class Ptt_Logger():
    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger('Ptt_Crawler')
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s-%(levelname)s-%(name)s-%(message)s\n')
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(stream_handler)
        file_handler = logging.FileHandler('Logs/crawler_log.log')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def critical(self, msg):
        self.logger.critical(msg)

    def log(self, msg):
        self.logger.log(msg)

    def exception(self, msg):
        self.logger.exception(msg)

    def setLevel(self, level):
        self.logger.setLevel(level)
