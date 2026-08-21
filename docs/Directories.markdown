# `tggen` directories

When you run the `tggen init original_data/` command, tggen copies the wav
files from the `original_data` directory into the `0_current` directory under a
new `tggen` directory. Under the `tggen` directory it also creates the
directories `1_utterance`, `2_word`, `3_phoneme` and `4_phone` which will
eventually contain the TextGrids corresponding to the wav files after adding
the next Tier after the one indicated by the directory name. The directory
structure looks like the listing below.

```
.
├── original_data/
│   ├── File001.wav
│   ├── File002.wav
│   └── ...
└── tggen/
    ├── 0_current/
    │   ├── File001.TextGrid
    │   ├── File001.wav
    │   ├── File002.TextGrid
    │   ├── File002.wav
    │   └── ...
    ├── 1_utterance/
    │   ├── File001.TextGrid
    │   ├── File002.TextGrid
    │   └── ...
    ├── 2_word/
    │   ├── File001.TextGrid
    │   ├── File002.TextGrid
    │   └── ...
    ├── 3_phoneme/
    │   ├── File001.TextGrid
    │   ├── File002.TextGrid
    │   └── ...
    └── 4_phone/
        ├── File001.TextGrid
        ├── File002.TextGrid
        └── ...
```

## Workflow

On running `init` `tggen` will only populate the `0_current` directory. The
others will remain empty. The initial TextGrids in `0_current` will have only
an `utterance` tier, which `tggen` will populate from either a `prompts.csv`
file or AAA prompt files that correspond to the individual files. 

`prompts.csv` should be placed in the top level directory or the path should be
specified in the `tggen.yaml` configuration file in the top level directory:

```
.                  
├── prompts.csv
├── tggen.yaml
├── original_data/
│   ├── File001.wav
│   ├── File002.wav
│   └── ...
└── tggen/
    ├── ...
```

### Running the `add` command

When you run the `add` command `tggen` checks which level of annotation is the
latest done and populates the next one. You should only run this command when
you are ready with the previous level of annotation. 

When running `add` `tggen` will copy the TextGrids from the `0_current`
directory to the lowest level empty directory under `tggen` and then add the
next Tier or annotation level to the TextGrids in `0_current`. This way
intermediate results are retained, should something go wrong with the process
or in case you want to redo a step in the annotation process.

`4_phone` directory does not regularly ever get filled. It exists for potential
future features.
