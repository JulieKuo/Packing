import logging
from logging.handlers import TimedRotatingFileHandler



class Log():
    def __init__(self):
        self.level_dict = {
            1: logging.DEBUG,
            2: logging.INFO,
            3: logging.ERROR,
            4: logging.WARNING,
            5: logging.CRITICAL,
        }


    def set_log(self, filepath: str = "logs/log.log", level: int = 2, freq: str = "D", interval: int = 50, backup: int = 2, name: str = "log"):
        # define log format and date format
        format_  = "%(asctime)s %(levelname)s %(message)s"
        time_format = "%Y-%m-%d %H:%M:%S"

        formatter = logging.Formatter(format_, time_format) # create a log formatter
        log_level = self.level_dict[level] # get log level based on the provided "level"

        # initialize the logger
        self.logger = logging.getLogger(name = name)
        self.logger.setLevel(log_level)

        # create a file handler for log rotation
        self.handler = TimedRotatingFileHandler(filename = filepath, when = freq, interval = interval, backupCount = backup, encoding = "utf-8")
        self.handler.setFormatter(formatter)

        # add the file handler to the logger
        self.logger.addHandler(self.handler)

        return self.logger
    

    def shutdown(self):
        self.logger.removeHandler(self.handler)  # remove log handlers
        del self.logger, self.handler # delete logger instances