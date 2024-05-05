"""Entry point for Phenoplier CLI."""
import phenoplier.cli as cli
from phenoplier.config import APP_NAME


def main():
    cli.app(prog_name=APP_NAME)


if __name__ == "__main__":
    main()
