## Environment Variables
# Python adds user site-packages to sys.path, which may cause lack of reproducibility if the user has installed Python packages outside Conda environments.
# One solution is to set the PYTHONNOUSERSITE environment variable to True. (https://stackoverflow.com/questions/70851048/does-it-make-sense-to-use-conda-poetry)
export PYTHONNOUSERSITE=True

# Create a minimal Conda environment
conda env create -f ./environment.yml
conda activate phenoplier-cli

# Poetry setup
poetry init
poetry install --no-root