# Environment Setup

To set up the development environment for this program, we provided a bootstrap script. Simply run this command at the root directory of the project:

```bash
. ./scripts/setup_env.sh
```

This script will use Conda to create a new virtual environment named "phenoplier-cli", with Poetry inside for Python package management.

If no errors occur, you can activate the environment by running the following command:

```bash
conda activate phenoplier-cli-dev
```

Then check if the environment is set up correctly by running the following command:

```bash
poetry run python -m phenoplier -v
```

You should see the version of the program being printed out.
