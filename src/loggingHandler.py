from logging import Handler
from rites.logger import get_sec_logger
import sys
import os

# Make sure the rites module is in the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

uvilogger = get_sec_logger("logs", "Uvicorn")

uvilogger.add_custom("uvicorn", "UVI", 117, 176, 255)  # Light blue
uvilogger.add_custom("uvicorn.access", "ACC", 128, 237, 153)  # Light green
uvilogger.add_custom("uvicorn.error", "UVE", 255, 105, 97)  # Light red
uvilogger.add_custom("fastapi", "API", 187, 134, 252)  # Purple


class RitesUvicornHandler(Handler):
    """Handler for regular logs"""
    def __init__(self):
        super().__init__()

    def emit(self, record):
        try:
            msg = self.format(record)

            uvilogger.custom(record.name, msg)
        except Exception as e:
            print(f"Error in default log handler: {e}")


class RitesAccessHandler(Handler):
    """Handler specifically for access logs"""
    def __init__(self):
        super().__init__()

    def emit(self, record):
        try:
            # For access logs, don't try to use the formatter at all
            # Just extract the raw message without trying to format it
            if hasattr(record, 'args') and record.args:
                # These are the elements of an access log
                try:
                    client_addr, request_line, status_code = record.args[:3]
                    msg = f"{client_addr} - \"{request_line}\" {status_code}"
                except:
                    msg = record.getMessage()
            else:
                msg = record.getMessage()

            uvilogger.custom("uvicorn.access", msg)
        except Exception as e:
            print(f"Error in access log handler: {e}")


def get_logging_config():
    """Get a logging config with separate handlers for different log types"""
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(message)s",
            },
        },
        "handlers": {
            "default": {
                "()": lambda: RitesUvicornHandler(),
                "level": "INFO",
            },
            "access": {
                "()": lambda: RitesAccessHandler(),
                "level": "INFO",
            },
        },
        "loggers": {
            "uvicorn": {"handlers": ["default"], "level": "INFO", "propagate": False},
            "uvicorn.error": {"handlers": ["default"], "level": "INFO", "propagate": False},
            "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
            "fastapi": {"handlers": ["default"], "level": "INFO", "propagate": False},
        },
    }
