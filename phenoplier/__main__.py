"""Entry point for Phenoplier CLI."""
from . import cli
from .config import settings


def main():
    cli.app(prog_name=settings.APP_NAME)


if __name__ == "__main__":
    main()
