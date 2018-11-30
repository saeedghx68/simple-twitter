import logging
import logging.handlers


class Logger(object):  # singleton object
    __instance = None

    def __new__(cls):
        if Logger.__instance is None:
            Logger.__instance = object.__new__(cls)
            # create logger
            names = [
                'error',
            ]
            Logger.__instance.loggers = {}
            for name in names:
                Logger.__instance._create_logger(name)

        return Logger.__instance

    def _create_logger(self, name):
        logger = logging.getLogger(name)
        formatter = logging.Formatter(
            "%(asctime)s, %(levelname)s :%(message)s",
            "%Y-%m-%d %H:%M:%S")
        file_handler = logging.handlers.TimedRotatingFileHandler(
            'logs/%s.log' % name,
            when='midnight',
            backupCount=3
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.setLevel(logging.INFO)
        self.loggers[name] = logger

    def _get_logger(self, name):
        return self.loggers.get(name, None)

    def write_log(self, name, message):
        logger = self._get_logger(name)
        if logger:
            logger.info(message)


global_logger = Logger()
