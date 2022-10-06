# CAST

Computer Assisted Segmentation Tools (CAST) is a helper toolkit for phonetic
analysis. Based on config files and metadata it generates a dumb segmentation
that can then be adjusted in Praat or other TextGrid editing programs.

CAST *does not* do forced alignment. There is no acoustic analysis of speech
under the hood, only some adjustable heuristics for selecting a reasonable guess
for where the speech is for the utterance and word levels and then a totally
rule-based segmentation based on a pronunciation dictionary.

CAST *does* provide a segmentation template that is meant to be easy for a human
annotator to adjust. For this reason all automatically generated segments are of
equal length within a given word.

CAST *does* do the writing and boundary creation for you. No need to go back and
correct typos in the transcription -- at least on the phonological level -- and
a good deal less carpal tunnel strains because of reduced number of mouse
clicks. And a significantly more relaxed feel about the segmentation process in
general.

## Files and directories

- cast/ is the directory that contains most of the processing logic.
- cast.py is the commandline interface for CAST.
- .gitignore tells git which directories and files to ignore.
- local_files/ is not included in the distribution, but it is ignored by git. If
  you are working on CAST with git, this is the place to put your local test
  files and generated results to keep git from seeing them.
- cast_exclude_example.yml is an example of an exclusion list. The file is
  commented to make it easier to create your own based on it. To avoid a host of
  issues, the format is Strict YAML rather than regular YAML. Refer to
  documentation [https://hitchdev.com/strictyaml/](here) for details of the
  format and the file itself for how fields are handled.
- cast_stable_conda_env.yaml is the specification for the conda/python virtual
  environment in which CAST runs. Probably easiest to build with mamba rather
  than conda.

## Code

CAST is written in Python with some external packages and configuration/setting
files in StrictYAML. Some of the code base (particularly ) is shared with SATKIT
and there is a possibility that CAST will become a submodule in SATKIT or that
there will be some other kind of integration to avoid code duplication.
