Installation
============

This document describes how to install the package.

Using pip
---------

Currently, the package is undergoing internal testing. The package is hosted on PyPI Test and can be installed using the following command:

.. code-block:: bash

   # Creating a new conda environment is recommended for dependency isolation.
   # Run this to create it: conda create -y -n phenoplier python=3.12
   pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple phenoplier

You should be able to verify the installation by running the following command:

.. code-block:: bash

   phenoplier -v

The current version should be displayed.
