import logging as pyLogging
import sys


class _MaxLevelFilter(object):
    def __init__(self, highest_log_level):
        self._highest_log_level = highest_log_level

    def filter(self, log_record):
        return log_record.levelno <= self._highest_log_level


class Logger:

    def __init__(self, app_name, logger_name):
        self.app_name = app_name
        self.logger_name = logger_name

        stream_format = '{app_name} %(asctime)s %(levelname)9s: %(message)s' \
            .format(app_name=app_name)

        logger = pyLogging.getLogger(logger_name)
        logger.setLevel(pyLogging.INFO)

        # All logs default to the format specified above
        log_stream_formatter = pyLogging.Formatter(stream_format)

        info_stream_handler = pyLogging.StreamHandler(sys.stdout)
        info_stream_handler.setLevel(pyLogging.INFO)
        info_stream_handler.setFormatter(log_stream_formatter)
        info_stream_handler.addFilter(_MaxLevelFilter(pyLogging.WARNING))

        error_stream_handler = pyLogging.StreamHandler(sys.stderr)
        error_stream_handler.setLevel(pyLogging.ERROR)
        error_stream_handler.setFormatter(log_stream_formatter)

        # Logger which outputs to StdOut/StdErr (local)
        logger.setLevel(pyLogging.DEBUG)
        logger.addHandler(info_stream_handler)
        logger.addHandler(error_stream_handler)
        logger.propagate = False

        self.logger = logger

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)
