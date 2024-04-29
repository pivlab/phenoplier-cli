import os
import tempfile
from pathlib import Path
import tomlkit

from phenoplier.constants.metadata import USER_SETTINGS_FILE

conf = {}

# Read settings from user_settings.toml
def load_user_settings():
    if not USER_SETTINGS_FILE.exists():
        raise FileNotFoundError("user_settings.toml not found in the user's home directory.")
    with open(USER_SETTINGS_FILE, "r") as f:
        return tomlkit.loads(f.read())


# Write final settings to config.toml
def save_config(config, file_path="config.toml"):
    with open(file_path, "w") as f:
        tomlkit.dump(config, f)
    print(f"Configuration saved to {file_path}")


# Main script functionality
def main():
    settings = load_user_settings()

    # Directory setups
    root_dir = settings.get("ROOT_DIR", str(Path(tempfile.gettempdir(), "phenoplier").resolve()))
    code_dir = Path(__file__).parent.parent.resolve()
    data_dir = Path(root_dir, "data").resolve()
    results_dir = Path(root_dir, "results").resolve()
    software_dir = Path(root_dir, "software").resolve()
    conda_envs_dir = Path(software_dir, "conda_envs").resolve()

    # Construct final configuration
    config = {
        "ROOT_DIR": root_dir,
        "CODE_DIR": code_dir,
        "DATA_DIR": data_dir,
        "RESULTS_DIR": results_dir,
        "SOFTWARE_DIR": software_dir,
        "CONDA_ENVS_DIR": conda_envs_dir
    }

    # Additional settings and paths can be constructed here based on user settings
    config.update({
        "GENERAL": {
            "LOG_CONFIG_FILE": Path(code_dir, "log_config.yaml").resolve()
        }
    })

    # Save the final configuration to TOML file
    save_config(config)


if __name__ == "__main__":
    main()
