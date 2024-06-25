# Package Publishing

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
phenoplier -v
```
