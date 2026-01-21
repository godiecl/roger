#  Copyright (c) 2025. Diego Urrutia-Astorga <durrutia@ucn.cl>

import datetime
import logging
import time
from contextlib import contextmanager
from typing import Generator, Optional

import humanize


@contextmanager
def benchmark(
    operation_name: Optional[str] = None, log: Optional[logging.Logger] = None
) -> Generator[None, None, None]:
    """Context manager to benchmark a block of code."""

    start: int = time.perf_counter_ns()
    try:
        yield
    finally:
        elapsed: int = time.perf_counter_ns() - start
        elapsed_microseconds = elapsed / 1_000
        delta = datetime.timedelta(microseconds=elapsed_microseconds)

        humanize_time = humanize.precisedelta(
            delta, minimum_unit="microseconds", format="%.2f"
        )

        if not log:
            log = logging.getLogger(__name__)

        if operation_name:
            log.debug(f"⏱️{operation_name} executed in {humanize_time}.")
        else:
            log.debug(f"⏱️executed in {humanize_time}.")
