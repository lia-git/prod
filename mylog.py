import logging
from logging.handlers import RotatingFileHandler

def fetch_logger(name):
    logger=logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    file_handler=RotatingFileHandler(f"/data/prod/logs/all.log",maxBytes=30*1024*1024,backupCount=3)
    file_handler.setLevel(logging.DEBUG)
    stream_handler=logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)

    stream_formatter=logging.Formatter(
        '%(asctime)-5s %(levelname)-4s %(name)-12s %(message)s')
    file_formatter=logging.Formatter(
        '{"time":"%(asctime)s", "name": "%(name)s", "lineno": "%(lineno)d","module": "%(module)s","funcName": "%(funcName)s", "level": "%(levelname)s", "message": "%(message)s"}'
    )
    file_handler.setFormatter(file_formatter)
    stream_handler.setFormatter(stream_formatter)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger


