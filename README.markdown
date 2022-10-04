# CAST

Computer Assisted Segmentation Tools (CAST) is a helper toolkit for phonetic analysis. Based on config files and metadata it generates a dumb segmentation that can then be adjusted in Praat or other TextGrid editing programs.

CAST *does not* do forced alignment. There is no acoustic analysis of speech under the hood, only some adjustable heuristics for selecting a reasonable guess for where the speech is for the utterance and word levels and then a totally rule-based segmentation based on a pronunciation dictionary.

CAST *does* provide a segmentation template that is meant to be easy for a human annotator to adjust. For this reason all automatically generated segments are of equal length within a given word.

CAST *does* do the writing and boundary creation for you. No need to go back and correct typos in the transcription -- at least on the phonological level -- and a good deal less carpal tunnel strains because of reduced number of mouse clicks. And a significantly more relaxed feel about the segmentation process in general.
