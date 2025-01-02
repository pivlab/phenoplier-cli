Installation
============

This document describes how to install the package.

Install from Test PyPI
---------

Currently, the package is undergoing internal testing. The package is hosted on PyPI Test and can be installed using the following command:

.. code-block:: bash

   # Creating a new conda environment is recommended for dependency isolation.
   conda create -y -n phenoplier-cli python=3.12
   conda activate phenoplier-cli
   pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple phenoplier

You should be able to verify the installation by running the following command:

.. code-block:: bash

   phenoplier -v

The current version should be displayed.

Install from source
---------

In case of any issues, installing the package from source would be an option. Clone the repository and install the package using the following commands:

.. code-block:: bash

   git clone git@github.com:pivlab/phenoplier-cli.git
   cd phenoplier-cli
   pip install .
   # Add environment variable to use the dev settings:
   # You need to do this before running phenoplier on every new terminal session.
   export ENV_FOR_DYNACONF="dev"

You should be able to verify the installation by running the following command:

.. code-block:: bash
   phenoplier -v

For this approach, creating a conda environment is also recommended.
