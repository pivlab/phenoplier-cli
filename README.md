## Introduction
This is a command-line interface (CLI) for the [PhenoPLIER](https://github.com/haoyu-zc/phenoplier?tab=readme-ov-file) project. PhenoPLIER is a flexible computational framework that combines gene-trait and gene-drug associations with gene modules expressed in specific contexts. This CLI program aims to provide a more user-friendly interface for users to interact with the PhenoPLIER project and integrate it into their own computational pipelines.

## Installation
For now, we recommend using a new conda environment to install and test out the package as it's still under development. To do so, run the following commands:
```bash
# Create a new conda environment
conda create -n "phenoplier-cli" python=3.12.0
# Activate the new conda environment
conda activate phenoplier-cli
# Install the package
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple phenoplier
```

If no errors occur, you can check if the package is installed correctly by running the following command:
```bash
phenoplier -v
```

## Data Preparation
The data downloader of this project is still under refinement. For lab members who have access to the data, simply download the data and put it either to the defualt directory `/tmp/phenoplier` or another place specified in the `user_settings.toml` config file (discussed in a later section). The directory structure should look like this:
```bash
(cli) ☁  phenoplier-cli [main] ⚡  ll /tmp/phenoplier
total 12K
drwxrwxr-x 10 haoyu haoyu 4.0K Apr 22 13:05 data
drwxrwxr-x  3 haoyu haoyu 4.0K Apr 22 14:24 results
drwxrwxr-x  6 haoyu haoyu 4.0K Apr 22 14:24 software
```
Ask the project developer for the data download method.

## Usage
### GLS
> **Prerequisites**: Set up necessary data according to instructions in the installation section.

This section shows how to use the GLS command. First, we can check the help message by running the following command:

```bash
phenoplier run regression -h
```

That will give you brief information about the command and its arguments. More detailed documentation will be added to this repo's WiKi page in the future.

Note that, before running the GLS command, you need to set up the environment by running the following command:

```bash
phenoplier init -p <project_name>
```

This command will create a configuration files named `user_settings.toml` and `internal_settings.toml` in the directory specified by the `-p` option. (If omitted, will use the current shell directory by default.) You can modify these files to set up your own environment to run the GLS command.

```bash
vim ./phenoplier_settings.toml

# Default phenoplier_settings.toml
ROOT_DIR = "/tmp/phenoplier"
```

```bash
vim ./internal_settings.toml

# Core Settings
# Directory stores input data
DATA_DIR = "@format {this.ROOT_DIR}/data"
# Directory stores output data
RESULT_DIR = "@format {this.ROOT_DIR}/result"
# Directory stores third-party applications
SOFTWARE_DIR = "@format {this.ROOT_DIR}/software"
CONDA_ENVS_DIR = "@format {this.SOFTWARE_DIR}/conda_envs"

# General Settings
[GENERAL]
BIOMART_GENES_INFO_FILE = "@format {this.DATA_DIR}/biomart_genes_hg38.csv.gz"
LOG_CONFIG_FILE = "@format {this.SRC_DIR}/log_config.yaml"
TERM_ID_LABEL_FILE = "@format {this.DATA_DIR}/term_id_labels.tsv.gz"
TERM_ID_XREFS_FILE = "@format {this.DATA_DIR}/term_id_xrefs.tsv.gz"
...
```

If you have access to the aforementioned lab data, you can download the data and put it in the directory specified by the `ROOT_DIR` variable in the `user_settings.toml` file. That way you should not need to modify the `internal_settings.toml` file anymore. If you have your own data directory structure, you can modify the `internal_settings.toml` file to set up the environment accordingly. Future iterations of this project will provide more detailed instructions and less cumbersome ways for setting up the environment.

Now you can try it out by running the following sample command:

```bash
phenoplier run regression \
           -p <project_dir> \
           -i <path_to_the_input_file> \
           -o <path_to_the_output_file> \
           --gene-corr-file <path_to_your_gene_corr_file> \
           --covars default (or other available options)
```
Please adjust the option arguments according to your own data and file paths.

## Development Environment Setup
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

You should see the version of the program printed out.

## Package Publishing
This project is managed by Poetry. To publish the package to PyPI. Poetry supports the use of PyPI and private repositories for package discovery and publishing. During this development phase, we will TestPyPI to publish the package.

First we need to save the credentials for the TestPyPI repository. Run the following command:
```bash
# Add the TestPyPI repository
poetry config repositories.test-pypi https://test.pypi.org/legacy/
# Add the TestPyPI token
poetry config pypi-token.test-pypi <Your_Test_PyPI_Token>
```

Then we can build and publish the package to TestPyPI by running the following command:
```bash
poetry build
poetry publish -r test-pypi
```

After the package is published, you can install using the pip command. Note that, for testing purposes, you may want to create a new virtual environment to install the package. Thus, instead of installing the package globally by running the above command, you can create a new virtual environment and install the package there:
```bash
python3 -m venv /tmp/phenoplier-env
source /tmp/phenoplier-env/bin/activate
python3 -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple phenoplier
```
(The --extra-index-url option is used to specify the default PyPI repository for dependencies, as packages such as and pandas are not available on TestPyPI.)

Check if the package is installed correctly by running the following command:
```bash
phenoplier -v
```

## Testing
In the root directory of the project, run the following command:
```bash
PYTHONPATH=. pytest -rs --color=yes test/
```
