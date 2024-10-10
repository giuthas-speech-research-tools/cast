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
Routines for dealing with exclusion lists.
"""

import csv
import logging
from contextlib import closing
from pathlib import Path
from typing import Union

from icecream import ic

from strictyaml import (
    Map, Optional, Seq, Str,
    YAMLError, load
)

from .configuration_classes import ExclusionList

_logger = logging.getLogger('cast.configuration')


def apply_exclusion_list(
        recordings: list[dict],
        exclusion_list: ExclusionList
) -> None:
    """
    Apply exclusion list to the list of Recordings.

    Parameters
    ----------
    recordings : list[Recording]
        the list of Recordings
    exclusion_list : Path
        _description_
    """
    if not exclusion_list:
        return

    for recording in recordings:
        filename = recording['filename']
        if filename in exclusion_list.files:
            ic('excluding due to name', filename)
            _logger.info('Excluding %s: File is in exclusion list.', filename)
            recording['excluded'] = True

        # The first condition sees if the whole prompt is excluded,
        # the second condition checks if any parts of the prompt
        # match exclusion criteria (for example excluding 'foobar ...'
        # based on 'foobar').
        prompt = recording['prompt']
        partials = [element
                    for element in exclusion_list.parts_of_prompts
                    if element in prompt]
        if prompt in exclusion_list.prompts or partials:
            ic('excluding due to prompt', filename)
            _logger.info(
                'Excluding %s. Prompt: %s matches exclusion list.',
                filename, prompt)
            recording['excluded'] = True


def load_exclusion_list(filepath: Union[Path, str]) -> ExclusionList | None:
    """
    If it exists, load the exclusion list from the given path.

    Parameters
    ----------
    filepath : Union[Path, str]
        Either a Path object or a string. If a string is passed, it is assumed
        to be a relative path.

    Returns
    -------
    ExclusionList|None
        The exclusion list or None if one was not read. If the file was a .csv
        file, there will be only files excluded, a .yaml or .yml gives more
        options.
    """
    if isinstance(filepath, str):
        filepath = Path(filepath)

    if filepath.suffix in ('.yaml', '.yml'):
        return read_exclusion_list_from_yaml(filepath)

    if filepath.suffix == '.csv':
        return read_file_exclusion_list_from_csv(filepath)


def read_exclusion_list_from_yaml(filepath: Path) -> ExclusionList:
    """
    Read a yaml exclusion list from filepath.

    If no exclusion list file is present, return an empty array
    after warning the user.
    """
    if filepath.is_file():
        with closing(open(filepath, 'r', encoding='utf-8')) as yaml_file:
            schema = Map({
                Optional("files"): Seq(Str()),
                Optional("prompts"): Seq(Str()),
                Optional("parts_of_prompts"): Seq(Str())
            })
            try:
                raw_exclusion_dict = load(yaml_file.read(), schema)
            except YAMLError as error:
                _logger.fatal("Fatal error in reading exclusion list at %s.",
                              str(filepath))
                _logger.fatal(str(error))
                raise
    else:
        _logger.warning(
            "Didn't find run exclusion list at %s.", str(filepath))
        _logger.warning(
            "Continuing regardless.")
        raw_exclusion_dict = {}

    exclusion_dict = raw_exclusion_dict.data

    return ExclusionList(
        files=exclusion_dict['files'],
        prompts=exclusion_dict['prompts'],
        parts_of_prompts=exclusion_dict['parts_of_prompts'])


def read_file_exclusion_list_from_csv(filepath: Path) -> ExclusionList:
    """
    Read a csv exclusion list from filepath.

    Read list of files (that is, Recordings) to be excluded from processing.
    """
    if filepath.is_file():
        with closing(open(filepath, 'r', encoding='utf-8')) as csvfile:
            reader = csv.reader(csvfile, delimiter='\t')
            # Throw away the second field - it is a comment for human readers.
            excluded_files = [row[0] for row in reader]
            _logger.info('Read exclusion list %s with %d names.',
                         str(filepath), len(excluded_files))
    else:
        excluded_files = []
        _logger.warning(
            "Did not find the exclusion list at %s. Proceeding anyhow.",
            str(filepath))

    return ExclusionList(files=excluded_files)
