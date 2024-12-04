Environment Setup
=================

To set up the development environment for this program, a bootstrap script is provided. Follow these steps to ensure the environment is configured correctly:

Step 1: Run the Setup Script
----------------------------

At the root directory of the project, execute the following command:

.. code-block:: bash

   . ./scripts/setup_env.sh

This script uses Conda to create a new virtual environment named ``phenoplier-cli`` and installs Poetry for Python package management within the environment.

Step 2: Activate the Virtual Environment
----------------------------------------

Once the setup script completes without errors, activate the environment by running:

.. code-block:: bash

   conda activate phenoplier-cli-dev

Step 3: Verify the Setup
------------------------

To confirm that the environment is correctly set up, run the following command:

.. code-block:: bash

   poetry run python -m phenoplier -v

If the setup is successful, the version of the program will be printed to the terminal.

Notes
-----

- Ensure that Conda and Poetry are installed on your system before running the setup script.
- If you encounter any errors during setup, refer to the project's documentation or troubleshooting guide for assistance.
