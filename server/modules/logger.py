import logging
import colorlog


class CustomLoggerMeta(type):
    _instance = None

    def __call__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


class CustomLogger(metaclass=CustomLoggerMeta):
    log = None

    def __init__(self, level=logging.DEBUG):
        self.log = logging.getLogger('custom_logger')
        self.log.setLevel(level)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        formatter = colorlog.ColoredFormatter(
            '%(log_color)s%(asctime)s - %(module)s - %(levelname)s - %(message)s',
            log_colors={
                'DEBUG': 'white',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red, bg_yellow',
            }
        )
        console_handler.setFormatter(formatter)
        self.log.addHandler(console_handler)
