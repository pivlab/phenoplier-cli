"""Entry point for Phenoplier CLI."""
from phenoplier import cli
from phenoplier.constants.metadata import APP_NAME

def main():
    cli.app(prog_name=APP_NAME)

if __name__ == "__main__":
    main()