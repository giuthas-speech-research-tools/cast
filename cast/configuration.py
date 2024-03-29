#
# Copyright (c) 2022-2023 Pertti Palo.
#
# This file is part of Computer Assisted Segmentation Tools
# (see https://github.com/giuthas-speech-research-tools/cast/).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# The example data packaged with this program is licensed under the
# Creative Commons Attribution-NonCommercial-ShareAlike 4.0
# International (CC BY-NC-SA 4.0) License. You should have received a
# copy of the Creative Commons Attribution-NonCommercial-ShareAlike 4.0
# International (CC BY-NC-SA 4.0) License along with the data. If not,
# see <https://creativecommons.org/licenses/by-nc-sa/4.0/> for details.
#
# When using the toolkit for scientific publications, please cite the
# articles listed in README.markdown. They can also be found in
# citations.bib in BibTeX format.
#
"""
Load configuration files.

File types handled by this module are strict yaml config files, different types
of exclusion lists, and pronunciation dictionaries.

A possible future addition is handling also the saving of strict yaml config
files.
"""
import csv
import sys
from contextlib import closing
from pathlib import Path
from typing import Union

from strictyaml import (
    Bool, Float, Map, Optional, ScalarValidator, Str, YAMLError, load)


class PathValidator(ScalarValidator):
    """
    Validate yaml representing a Path.

    Please note that empty fields are interpreted as not available and
    represented by None. If you want to specify current working directory, use
    '.'
    """

    def validate_scalar(self, chunk):
        if chunk.contents:
            return Path(chunk.contents)
        return None


def read_config_file(filepath: Union[Path, str, None] = None) -> dict:
    """
    Read the config file from filepath.

    If filepath is None, read from the default file 'cast_config.yml'.
    In both cases if the file does not exist, report this and exit.
    """
    if filepath is None:
        filepath = Path('cast_config.yml')
    elif isinstance(filepath, str):
        filepath = Path(filepath)

    if filepath.is_file():
        with closing(open(filepath, 'r', encoding="utf-8")) as yaml_file:
            schema = Map({
                "data source": Str(),
                "speaker id": Str(),
                "data directory": PathValidator(),
                "outputfile": PathValidator(),
                Optional("output_dirname"): PathValidator(),
                "flags": Map({
                    "detect beep": Bool(),
                    "test": Bool()
                }),
                "tiers": Map({
                    "file": Bool(),
                    "utterance": Bool(),
                    "word": Bool(),
                    "phoneme": Bool(),
                    "phone": Bool()
                }),
                "tier names": Map({
                    "file": Str(),
                    "word": Str(),
                    "utterance": Str(),
                    "phoneme": Str(),
                    "phone": Str()
                }),
                "exclusion list": PathValidator(),
                "pronunciation dictionary": PathValidator(),
                "word guess": Map({
                    "begin": Float(),
                    "end": Float()
                })
            })
            try:
                config_dict = load(yaml_file.read(), schema)
            except YAMLError as error:
                print(f"Fatal error in reading {filepath}:")
                print(error)
                sys.exit()
    else:
        print(f"Didn't find {filepath}. Exiting.".format(str(filepath)))
        sys.exit()
    return config_dict.data


def read_exclusion_list(filepath: Path) -> dict:
    """
    Read the exclusion list from filepath.

    If no exclusion list file is present, return an empty array
    after warning the user.
    """
    if filepath.is_file():
        with closing(open(filepath, 'r', encoding="utf-8")) as yaml_file:
            yaml = load(yaml_file.read())
            exclusion_dict = yaml.data
    else:
        exclusion_dict = {}
        print(
            f"Did not find the exclusion list at {filepath}. Proceeding anyhow.")
    return exclusion_dict


def read_na_list(dirpath: Path) -> list[str]:
    """
    Read the old style exclusion list from na_list.txt.

    If no exclusion list file is present, return an empty array
    after warning the user.
    """
    na_file = dirpath.joinpath('na_list.txt')
    if na_file.is_file():
        na_list = [line.rstrip('\n')
                   for line in open(na_file, encoding="utf-8")]
    else:
        na_list = []
        print("Didn't find na_list.txt. Proceeding anyhow.")
    return na_list


def read_pronunciation_dict(filepath: Union[Path, str]) -> dict:
    """
    Read the pronuciation dictionary and return it as a dict.

    The file is assumed to be in tab separated format and to 
    contain one word on each line followed by the X-SAMPA transcription
    of the expected pronunciation (phonological transcription).

    Returns a dict where each entry is a list of phonomes.
    """
    if isinstance(filepath, str):
        filepath = Path(filepath)

    pronunciation_dict = {}
    if filepath.is_file():
        with closing(open(filepath, 'r', encoding="utf-8")) as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            pronunciation_dict = {row[0]: list(filter(None, row[1:]))
                                  for row in reader}
        return pronunciation_dict
    else:
        print(f"Didn't find {pronunciation_dict}. Exiting.")
        sys.exit()
