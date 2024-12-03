Data Preparation
=================

Before using this software, you need to prepare the required data. You can use the built-in ``get`` command to do this:

.. code-block:: bash

   $ phenoplier get -h

   Usage: phenoplier get [OPTIONS] MODE:{test_data|full_data}

    Download necessary data for running PhenoPLIER's pipelines.

   ╭─ Arguments ───────────────────────────────────────────────────────────────────────────────────╮
   │ *    mode      MODE:{test_data|full_data}  [default: None] [required]                         │
   ╰───────────────────────────────────────────────────────────────────────────────────────────────╯
   ╭─ Options ─────────────────────────────────────────────────────────────────────────────────────╮
   │ --project-dir  -p      PATH  Path to output the initialized project files. Default to current │
   │                              directory.                                                       │
   │                              [default: /home/haoyu/_database/projs/phenoplier-cli]            │
   │ --help         -h            Show this message and exit.                                      │
   ╰───────────────────────────────────────────────────────────────────────────────────────────────╯

Run the command ``phenoplier get full_data`` and wait for it to complete. Once this process is finished, you will have all the necessary data prepared. The final step before actually running our pipelines is to learn how to create and customize project configurations to fit your needs.
