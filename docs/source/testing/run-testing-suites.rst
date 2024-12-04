Running the Testing Suites
===================================

To verify the functionality of the project, you can run the included testing suites using `pytest`. 

Follow these steps:

1. Navigate to the root directory of the project.
2. Execute the following command:

   .. code-block:: bash

      PYTHONPATH=. pytest -rs --color=yes test/

Explanation of the Command
--------------------------

- ``PYTHONPATH=.``: Ensures that the current project directory is included in the Python module search path.
- ``pytest``: The testing framework used to run the test cases.
- ``-rs``: Displays a summary of any skipped or failed tests at the end of the test run.
- ``--color=yes``: Enables colored output for better readability of test results.
- ``test/``: Specifies the directory containing the test suite to execute.

Expected Outcome
----------------

If all tests pass, you will see a summary indicating the number of tests executed and their statuses. Any failures or skipped tests will also be detailed in the output.

Notes
-----

- Ensure all dependencies are installed in the active environment before running the tests.
- For detailed test output, you can add the ``-v`` option to the command.
- Use ``pytest --help`` to explore additional options for customizing your test runs.

