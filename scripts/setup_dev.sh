# Create development environment for the project

conda env create -f environment.yml -n phenoplier-cli
conda activate phenoplier-cli
poetry install --no-root
