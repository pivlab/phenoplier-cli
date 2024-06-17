import tempfile
import os
from pathlib import Path
from dynaconf import Dynaconf
from tomlkit import parse

pacakge_toml_file = Path(__file__).parent.parent.resolve() / "pyproject.toml"
with open(pacakge_toml_file) as f:
    package_toml = parse(f.read())
    _PACKAGE_NAME = package_toml["tool"]["poetry"]["name"]
    _PACKAGE_VERSION = package_toml["tool"]["poetry"]["version"]

# Config files
SETTINGS_FILES = ["phenoplier_settings.toml"]

# If in test or dev environment, load the settings from the templates folder, instead of the user
# "init"ed project folder to simplify setup process
env = os.getenv("ENV_FOR_DYNACONF")
env_settings = []
if env == "dev" or env == "test":
    settings_dir = Path(__file__).resolve().parent / "templates"
    env_settings = [settings_dir / file for file in SETTINGS_FILES]

# Initialize setting for NumExpr
num_cores = os.cpu_count()
os.environ["NUMEXPR_MAX_THREADS"] = f"{num_cores // 2}"

# The environment variables name supersede these settings
# Prefix the environment variables with `$_PACKAGE_NAME` to automatically load them
# E.g. `export {$_PACKAGE_NAME}_FOO=bar` will load `FOO=bar` in the settings

settings = Dynaconf(
    envvar_prefix="PHENOPLIER",
    # TODO: Append the curr_dir settings to override the default settings
    settings_files=env_settings,

    APP_NAME=_PACKAGE_NAME,
    APP_VERSION=_PACKAGE_VERSION,
    CURRENT_DIR=os.getcwd(),

    # Specifies the main directory where all data and results generated are stored.
    # When setting up the environment for the first time, input data will be
    # automatically downloaded into a subfolder of ROOT_DIR. If not specified, it
    # defaults to the 'phenoplier' subfolder in the temporary directory of the
    # operating system (i.e. '/tmp/phenoplier' in Unix systems).
    #
    ROOT_DIR=Path(tempfile.gettempdir(), _PACKAGE_NAME).resolve(),
    # Directory contains the git repository
    REPO_DIR=Path(__file__).resolve().parent.parent,
    # Directory contains the source code
    SRC_DIR=Path(__file__).resolve().parent,
    # Path to the log configuration file
    LOG_CONFIG_FILE="@format {this.SRC_DIR}/log_config.yaml",
    # Directory contains the templates
    TEMPLATE_DIR="@format {this.SRC_DIR}/templates/",
    # Directory contains the tests
    TEST_DIR="@format {this.REPO_DIR}/test/",
    # Directory to put test outputs
    TEST_OUTPUT_DIR=Path("/tmp/" + _PACKAGE_NAME + "_test_output/").resolve(),
    # Directory for cached data
    CACHE_DIR="@format {this.REPO_DIR}/.cache/",
)
