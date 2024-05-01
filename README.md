## Introduction
This is a command-line interface (CLI) for the [PhenoPLIER](https://github.com/haoyu-zc/phenoplier?tab=readme-ov-file) project. PhenoPLIER is a flexible computational framework that combines gene-trait and gene-drug associations with gene modules expressed in specific contexts. This CLI program aims to provide a more user-friendly interface for users to interact with the PhenoPLIER project and integrate it into their own computational pipelines.

## Installation
For now, we recommend using a new conda environment to install and test out the package as it's still under development. To do so, run the following command at the root directory of the project:
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
python3 -m phenoplier -v
```

## Usage
### GLS
This section shows how to use the GLS command. First, we can check the help message by running the following command:

```bash
python3 -m phenoplier run gls -h
```

That will give you brief information about the command and its arguments. More detailed documentation will be added to this repo's WiKi page in the future. Here is an example of how to run the GLS command:

```bash
python3 -m phenoplier run gls \
        -i /media/haoyu/extradrive1/alpine_data/pivlab/data/phenoplier/results/gls/null_sims/twas/smultixcan/random.pheno17-gtex_v8-mashr-smultixcan.txt \
        -o /media/haoyu/extradrive1/alpine_data/pivlab/data/phenoplier/results/gls/null_sims/phenoplier/1000g_eur/covars/gls-gtex_v8_mashr-sub_corr/random.pheno17-gls_phenoplier.tsv.gz \
        --gene-corr-file /media/haoyu/extradrive1/alpine_data/pivlab/data/phenoplier/results/gls/gene_corrs/cohorts/1000g_eur/gtex_v8/mashr/gene_corrs-symbols-within_distance_5mb.per_lv/ \
        --covars "gene_size gene_size_log gene_density gene_density_log"
```
Please adjust the option arguments according to your own data and file paths.

## Development Environment Setup
To set up the development environment for this program, we provided a bootstrap script. Simply run this command at the root directory of the project:

```bash
. ./scripts/setup_dev.sh
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
python3 -m phenoplier -v
```

## Testing
In the root directory of the project, run the following command:
```bash
poetry run pytest
```

## Roadmap
- [ ] Build up CLI
- [ ] Port core logic from the Jupyter notebook to the CLI
- [ ] Add interactive mode to setup the environment