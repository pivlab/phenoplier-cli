.. _data-projection:

Data Projection
====================

This section shows how to use the `project` command to convert data into the latent space of a specified model.

.. code-block:: bash

   phenoplier project -h
                                                                                                                                                                                                                                                                                                               
      Usage: phenoplier project [OPTIONS] COMMAND [ARGS]...                                                                                                                                                                                                                                                      
                                                                                                                                                                                                                                                                                                               
      projects input data into the specified representation space.                                                                                                                                                                                                                                               
                                                                                                                                                                                                                                                                                                               
   ╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
   │ --help  -h        Show this message and exit.                                                                                                                                                                                                                                                            │
   ╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
   ╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
   │ to-multiplier   Projects new data into the MultiPLIER latent space.                                                                                                                                                                                                                                      │
   ╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

Right now, the `project` command supports projecting data into the MultiPLIER representation space:

.. code-block:: bash

   phenoplier project to-multiplier -h
                                                                                                                                                                                                                                                                                                               
      Usage: phenoplier project to-multiplier [OPTIONS]                                                                                                                                                                                                                                                          
                                                                                                                                                                                                                                                                                                               
      Projects new data into the MultiPLIER latent space.                                                                                                                                                                                                                                                        
                                                                                                                                                                                                                                                                                                               
   ╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
   │ *  --input-file   -i      PATH  Input data in .rds format to be projected into the MultiPLIER model. Gene symbols are expected in rows. The columns could be conditions/samples [default: None] [required]                                                                                               │
   │    --output-file  -o      PATH  File path where the projected data (pandas.DataFrame) will be written to. Default to the same directory with the same name as the input file, but in .pkl format. [default: None]                                                                                     │
   │    --project-dir  -p      PATH  Path to project directory which contains the 'phenoplier_settings.toml' file. Default to the current directory. Run 'phenoplier init' to create the project. [default: /home/haoyu/_database/projs/phenoplier-cli]                                                       │
   │    --help         -h            Show this message and exit.                                                                                                                                                                                                                                              │
   ╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

In addition, this functionality is exposed as a Python API:

.. code-block:: python
   """
   Module multiplier.py
   """

   def transform(
      y: pd.DataFrame,
      multiplier_compatible: bool = True,
   ) -> pd.DataFrame:
      """Projects a gene dataset into the MultiPLIER model.

      This code is a reimplementation in Python of the function GetNewDataB
      (https://github.com/greenelab/multi-plier/blob/v0.2.0/util/plier_util.R),
      more suitable and convenient for the PhenoPLIER project (almost entirely
      written in Python).

      It basically row-normalizes (z-score) the given dataset, keeps only the
      genes in common with the MultiPLIER model, and adds the missing ones as
      zeros (mean).

      Args:
         y:
               The new data to be projected. Gene symbols are expected in rows.
               The columns could be conditions/samples, but in the PhenoPLIER
               context they could also be traits/diseases or perturbations
               (Connectivity Map).
         multiplier_compatible:
               If True, it will try to be fully compatible with the GetNewDataB
               function in some situations (for instance, if the new data
               contains NaNs).

      Returns:
         A pandas.DataFrame with the projection of the input data into the
         MultiPLIER latent space. The latent variables of the MultiPLIER
         model are in rows, and the columns are those of the input data
         (conditions, traits, drugs, etc).


The following code snippet shows how to use the `project` function to project data into the MultiPLIER latent space:

.. code-block:: python

   import phenoplier.multiplier as multiplier

   # input data
   input_data = ...
   # project data
   proj_data = multiplier.transform(input_data)
   # save projected data
   projected_data.to_pickle("projected_multiplier_data.pkl")
