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
from contextlib import closing
from pathlib import Path
import sys


def add_prompt_info(table: list) -> None:
    """
    Check for existence of prompts and add the prompt to table.

    If the prompt file does not exist, set the flag 'excluded' to True.

    Works in place, so does not return anything.
    """
    for entry in table:
        if not entry['prompt_path'].is_file():
            filename = entry['filename']
            print(f'Excluding {filename}. Recording has no prompt file.')
            entry['excluded'] = True
        else:
            with closing(open(entry['prompt_path'], 'r',
                              encoding='utf8')) as prompt_file:
                prompt = prompt_file.readline().strip()
                entry['prompt'] = prompt


def check_and_load_aaa_meta(
        speaker_id: str, directory: Path,
        test: bool, require_ultrasound: bool = False, ) -> list[dict]:
    """
    Check and load Trial metadata generated by AAA.

    Parameters
    ----------
    speaker_id : str
        Speaker id to assign. This overrides what ever is written in the AAA
        generated prompt file.
    directory : Path
        Path to the recordings.
    test : bool
        If we are running in test mode.
    require_ultrasound : bool, optional
        Should recordings be excluded if there is no ultrasound file present, by
        default False

    Returns
    -------
    list[dict]
        List of dicts containing the read and generated metadata.
    """
    # Since we are concerned with audio annotation, wav files
    # determine the name list for all other files.
    wav_files = sorted(directory.glob('*.wav'))
    if len(wav_files) < 1:
        print(f"Didn't find any sound files to concatenate in {directory}.")
        sys.exit()

    # for test runs do only first ten files:
    if test and len(wav_files) >= 10:
        wav_files = wav_files[:10]

    prompt_files = sorted(directory.glob('*.txt'))
    if len(prompt_files) < 1:
        print(f"Didn't find any prompt files in {directory}.")
        sys.exit()

    # initialise table with the speaker_id and name repeated, wav_file name
    # from the list, and other fields empty

    # TODO: consider making this a dataclass
    table = [{
        'excluded': False,
        'filename': wavfile.stem,
        'wav_path': wavfile,
        'prompt_path': wavfile.with_suffix('.txt'),
        'ultra_path': wavfile.with_suffix('.ult'),
        'id': wavfile.stem,
        'speaker': speaker_id,
        'sliceBegin': 'n/a',
        'begin': 'n/a',
        'end': 'n/a',
        'prompt': 'n/a'}
        for wavfile in wav_files]

    if require_ultrasound:
        for entry in table:
            filename = entry['filename']
            if not entry['ultra_path'].is_file():
                print(
                    f"Excluding {filename}. Recording has no ultrasound file.")
                entry['excluded'] = True

    add_prompt_info(table)

    return table
