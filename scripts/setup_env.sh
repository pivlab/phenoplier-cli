# This script is used to set up the environment for PhenoPLIER CLI

# User configurations, feel free to modify
CONDA_ENV_NAME="phenoplier-cli-dev"
# User configurations end

# Create a minimal Conda environment
conda env create -f ./environment.yml -n $CONDA_ENV_NAME
# Activate the Conda environment to install dependencies using Poetry
conda init bash
source ~/.bashrc
conda activate $CONDA_ENV_NAME

# Install Python dependencies
poetry init
poetry install

# Deactivate the Conda environment
conda deactivate

echo "PhenoPLIER CLI environment is set up. Conda environment name: $CONDA_ENV_NAME."
echo "Please activate the environment using 'conda activate $CONDA_ENV_NAME'."
