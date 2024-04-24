## Introduction
In early iterations of this project, this README file is used to provide instructions for developers to install and run the project. As the project evolved, the development contents should be moved to the project's wiki and this README file should be used to provide information for end-users.

## Installation
To set up the environment for this program with default settings, we provided a bootstrap script. Simply run this command at the root directory of the project:

```bash
./init.sh
```

This script will use Conda to create a new virtual environment named "phenoplier-cli", with Poetry inside for Python package management.

If no errors occur, you can activate the environment by running the following command:

```bash
conda activate phenoplier-cli
```

Then check if the environment is set up correctly by running the following command:

```bash
poetry run python -m phenoplier -v
```

You should see the version of the program printed out.

## Usage


## Testing
In the root directory of the project, run the following command:
```bash
poetry run pytest
```

## Roadmap
- [ ] Build up CLI
- [ ] Port core logic from the Jupyter notebook to the CLI
- [ ] Add interactive mode to setup the environment