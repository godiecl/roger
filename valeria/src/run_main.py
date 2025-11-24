import logging

from dotenv import load_dotenv

from utils.benchmarking import benchmark
from utils.logger import configure_logging


def main():
    log.info("🚀 Application started successfully.")
    log.info("🏁 Application finished execution.")


if __name__ == "__main__":
    configure_logging(log_level=logging.DEBUG)
    log = logging.getLogger(__name__)

    with benchmark("main", log):
        # load environment variables from .env file
        if load_dotenv():
            log.info("✅.env file loaded successfully.")
        else:
            raise EnvironmentError("💀.env file not found or could not be loaded.")
        # showtime!
        main()
