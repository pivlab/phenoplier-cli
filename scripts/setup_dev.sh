# This script is used to set up the environment for PhenoPLIER CLI

# User configurations, feel free to modify
CONDA_ENV_NAME="phenoplier-cli-dev"
# User configurations end

# Create a minimal Conda environment
conda env create -f ./environment.yml -n $CONDA_ENV_NAME
# Activate the Conda environment to install dependencies using Poetry
conda activate $CONDA_ENV_NAME

# Install Python dependencies
poetry init
poetry install --no-root

# Exit the Conda environment
conda deactivate

echo ""
echo "PhenoPLIER CLI environment is set up. Conda environment name: $CONDA_ENV_NAME."
echo "To activate the environment, run: conda activate $CONDA_ENV_NAME"
