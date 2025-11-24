#  Copyright (c) 2025. Diego Urrutia-Astorga <durrutia@ucn.cl>

import logging
from typing import Union

import coloredlogs
from typeguard import typechecked


@typechecked
def configure_logging(log_level: Union[int, str] = logging.INFO) -> None:
    """Configure logging with colores output."""

    # the log format
    log_format = "%(asctime)s [%(levelname)8s] %(name)s:%(lineno)d (%(process)d/%(threadName)s) - %(message)s"

    # hide matplotlib
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)
    logging.getLogger("httpcore.connection").setLevel(logging.WARNING)
    logging.getLogger("httpcore.http11").setLevel(logging.WARNING)
    logging.getLogger("openai._base_client").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("numba.core").setLevel(logging.WARNING)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("pygeohash.pygeohash.geohash").setLevel(logging.WARNING)

    coloredlogs.install(
        level=log_level,
        fmt=log_format,
        level_styles={
            "DEBUG": {"color": "black", "bright": True},
            "INFO": {"color": "green"},
            "WARNING": {"color": "magenta"},
            "ERROR": {"color": "red"},
            "CRITICAL": {"color": "red", "bold": True, "background": "white"},
        },
        field_styles={
            "asctime": {"color": "yellow"},
            "levelname": {"bold": True},
            "name": {"color": "blue", "bold": True},
            "lineno": {"color": "magenta"},
            "process": {"color": "green"},
            "threadName": {"color": "cyan"},
            "message": {"color": "white"},
        },
        milliseconds=True,
    )
