# This script is used to set up the development environment for PhenoPLIER CLI
# Run this at the root of the repository:
# source scripts/dev_setup.sh

# Set the executor of commands to "bash" (so commands are run in the terminal)
export PHENOPLIER_JOBS_EXECUTOR="bash"

# Set the root directory of PhenoPLIER source code
export PHENOPLIER_CODE_DIR="./"

# Append the PhenoPLIER code lib to the PYTHONPATH
export PYTHONPATH="${PHENOPLIER_CODE_DIR}/libs:${PYTHONPATH}"

# Set test folder
export PHENOPLIER_TEST_DIR="${PHENOPLIER_CODE_DIR}/test"

# Load the PhenoPLIER configuration
eval `python libs/conf.py`