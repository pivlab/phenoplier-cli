# Data Preparation

You need to get the required data ready before using this software. You can use the built-in `get` command to do so:

```bash
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
```

Run `phenoplier get full_data` and wait for it to complete. After, all preparation works are done! Feel free to check which pipeline you are interested in and give it a try.
