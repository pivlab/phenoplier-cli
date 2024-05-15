"""Entry point for Phenoplier CLI."""
from . import cli
from .config import settings
import sys


def main():
    cli.app(prog_name=settings.APP_NAME)
    sys.exit()


if __name__ == "__main__":
    main()
