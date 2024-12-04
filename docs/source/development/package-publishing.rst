Package Publishing
===================

This project is managed using Poetry, which simplifies the process of publishing to PyPI and private repositories. During the development phase, the package will be published to TestPyPI for testing purposes.

Step 1: Configure TestPyPI Credentials
---------------------------------------

Before publishing, save your TestPyPI credentials by running the following commands:

.. code-block:: bash

   # Add the TestPyPI repository
   poetry config repositories.test-pypi https://test.pypi.org/legacy/
   # Add the TestPyPI token
   poetry config pypi-token.test-pypi <Your_Test_PyPI_Token>

Replace ``<Your_Test_PyPI_Token>`` with your actual TestPyPI token.

Step 2: Build and Publish the Package
--------------------------------------

To build the package and publish it to TestPyPI, execute the following commands:

.. code-block:: bash

   poetry build
   poetry publish -r test-pypi

Step 3: Install the Package for Testing
----------------------------------------

After publishing, you can install the package from TestPyPI using pip. It is recommended to test the installation in a new virtual environment. Follow these steps:

1. Create and activate a new virtual environment:

   .. code-block:: bash

      python3 -m venv /tmp/phenoplier-env
      source /tmp/phenoplier-env/bin/activate

2. Install the package from TestPyPI:

   .. code-block:: bash

      python3 -m pip install --index-url https://test.pypi.org/simple/ \
         --extra-index-url https://pypi.org/simple phenoplier

   The ``--extra-index-url`` option ensures dependencies not available on TestPyPI are pulled from the default PyPI repository.

Step 4: Verify the Installation
--------------------------------

To confirm that the package is installed correctly, run:

.. code-block:: bash

   phenoplier -v

If the setup is successful, the package version will be displayed.

Notes
-----

- Make sure Poetry is installed and properly configured on your system.
- Use the TestPyPI environment for testing only. For production, publish the package to the official PyPI repository.
- For more information about managing Python packages with Poetry, refer to the Poetry documentation.
