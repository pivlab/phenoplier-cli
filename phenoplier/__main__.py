"""Entry point for Phenoplier CLI."""
from phenoplier import cli
from phenoplier.config import settings
from phenoplier.log import config_logger
import sys


def main():
    cli.app(prog_name=settings.APP_NAME)
    sys.exit()


if __name__ == "__main__":
    config_logger()
    main()
