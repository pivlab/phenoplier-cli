# Project Configuration

PhenoPLIER allows users to create per-project configurations, enabling flexible management of separate projects. To initialize a PhenoPLIER project, run the following command:

```bash
phenoplier init -p <path_to_desired_directory>
```

A configuration file named `phenoplier_settings.toml` will be created in the directory specified by the -p option. If the -p option is omitted, the current shell directory will be used by default. This configuration file contains comprehensive settings for the entire CLI program.

We recommend using the default settings initially to get familiar with the software. Once you're comfortable, you can adjust the configurations as needed. Here's a quick look at the config file:

<pre class="language-bash"><code class="lang-bash">vim phenoplier_settings.toml


# Core Settings
# Base working directory for the project, where data, results, and software are stored
ROOT_DIR = "/tmp/phenoplier"
# Directory that stores input data
DATA_DIR = "@format {this.ROOT_DIR}/data"
# Directory that stores output data
RESULT_DIR = "@format {this.ROOT_DIR}/results"
<strong># ...(omitted)
</strong># The most important setting is ROOT_DIR, which specifies the root working directory for PhenoPLIER. By default, all data and results are stored in this directory with the following hierarchy.
</code></pre>

You may have noticed the `@format token` syntax being used. It's a workaround to access other entries defined in the same file before the use point. For more information, consult Dynaconf's document about [Dynamic Variables](https://www.dynaconf.com/dynamic/). Dynaconf is a configuration manager python pakcage that is used in this project.

Here's the directory structure specified by the generated default config file:

```bash
/tmp/phenoplier # ROOT_DIR
├── data        # DATA_DIR
└── results     # RESULT_DIR
```

Refer to the default config file and adjust it to fit your needs. In future iterations of this software, we will provide a more convenient way to configure the parameters. We recommend leave the settings as default and move on to the [next section](https://github.com/pivlab/phenoplier-cli/wiki/\_new) of this tutorial.
