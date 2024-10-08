#
# Copyright (c) 2022-2024 Pertti Palo.
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
Define and process CAST command line commands.
"""
from enum import Enum
from pathlib import Path
import sys
from .clean_textgrids import remove_empty_intervals_from_textgrids
from .concatenate import concatenate_wavs

from .configuration import read_pronunciation_dict
from .extract import extract_textgrids
from .path_functions import initialise_dataset
from .textgrid_functions import add_tiers


class ExtendedEnum(Enum):
    """
    Enum whose values can be listed easily.
    """

    @classmethod
    def values(cls) -> list:
        """
        Class method which returns a list of the Enum's values.

        Returns
        -------
        list
            A list of the Enum's values.
        """
        return list(map(lambda c: c.value, cls))


class CommandStrings(ExtendedEnum):
    """
    Commands accepted by CAST as strings.
    """
    ADD = 'add'
    CONCATENATE = 'concatenate'
    EXTRACT = 'extract'
    INITIALISE = 'init'
    REMOVE_DOUBLE_WORD_BOUNDARIES = 'remove-double-word-boundaries'


def process_command(command: CommandStrings, path: Path, config_dict: dict):
    """
    Run a CAST command.

    Parameters
    ----------
    command : CommandStrings
        The command to be run.
    path : Path
        What to run the command on.
    config_dict : dict
        Configuration to run the command with.
    """

    if command is CommandStrings.INITIALISE:
        initialise_dataset(path, config_dict)
    elif command is CommandStrings.ADD:
        pronunciation_dict = None
        if not config_dict['flags']['only words']:
            pronunciation_dict = read_pronunciation_dict(
                config_dict['pronunciation dictionary'])
        add_tiers(path, config_dict, pronunciation_dict=pronunciation_dict)
    elif command is CommandStrings.CONCATENATE:
        pronunciation_dict = None
        if not config_dict['flags']['only words']:
            pronunciation_dict = read_pronunciation_dict(
                config_dict['pronunciation dictionary'])
        concatenate_wavs(
            path, config_dict, pronunciation_dict)
    elif command is CommandStrings.REMOVE_DOUBLE_WORD_BOUNDARIES:
        if not config_dict['output_dirname']:
            print(
                'Fatal: No output directory for new textgrids specified in '
                'config file.')
        remove_empty_intervals_from_textgrids(
            Path(path), Path(config_dict['output_dirname']))
    elif command is CommandStrings.EXTRACT:
        extract_textgrids(Path(path), Path(config_dict['outputfile']))
    else:
        print(f"Did not recognise the command {command}. Exiting.")
        sys.exit()
