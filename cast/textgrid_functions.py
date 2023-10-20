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
textgrid_functions contains functions for generating and modifying TextGrid objects.
"""
import pprint
import sys
from typing import Optional
from pathlib import Path

import numpy as np
from textgrids import TextGrid

from .meta.aaa_meta import check_and_load_aaa_meta
from .meta.csv_meta import check_and_load_csv_meta
from .meta.rasl_meta import check_and_load_rasl_meta

pp = pprint.PrettyPrinter(indent=4)


def add_tiers(path, config_dict: dict, pronunciation_dict: dict = None,
              csv_meta_file: Optional[str] = None) -> None:

    speaker_id = config_dict['speaker id']
    test = config_dict['test']

    if isinstance(path, str):
        path = Path(path)

    if path.is_file:
        if path.suffix == ".TextGrid":
            textgrid = TextGrid(str(path))
            add_tiers_to_textgrid(textgrid, config_dict, pronunciation_dict)
            textgrid.write(str(path))
        else:
            print(f"Unknown file type: {path.suffix}. Exiting.")
            sys.exit()
    elif path.is_dir:
        data_source = config_dict['data source']
        table = {}
        if data_source == 'AAA':
            table = check_and_load_aaa_meta(
                speaker_id, path, test)
        elif data_source == 'RASL':
            table = check_and_load_rasl_meta(speaker_id, path, test)
        elif data_source == 'csv':
            table = check_and_load_csv_meta(
                speaker_id, path, test, csv_meta_file)
        else:
            print(f"Unknown data source: {data_source}. Exiting.")
            sys.exit()
        for item in table:
            textgrid = TextGrid((item['filename'] + ".TextGrid"))
            add_tiers_to_textgrid(textgrid, config_dict, pronunciation_dict)
            textgrid.write((item['filename'] + ".TextGrid"))


def add_tiers_to_textgrid(textgrid: TextGrid, table: list, config_dict: dict,
                          pronunciation_dict: dict = None) -> None:
    """
    Add Tiers to a TextGrid

    Parameters
    ----------
    textgrid : TextGrid
        The Tiers will be added to this TextGrid
    table : List
        _description_
    config_dict : Dict
        Configuration dictionary
    pronunciation_dict : Dict, optional
        Pronunciation dictionary -- not needed if only generating to the word level, by default None
    """
    begin_coeff = config_dict['word guess']['begin']
    end_coeff = config_dict['word guess']['end']

    if config_dict['flags']['utterance'] or config_dict['flags']['word']:
        textgrid.interval_tier_from_array(
            config_dict['tier names']['word'], words)
    if config_dict['flags']['phoneme']:
        textgrid.interval_tier_from_array(
            config_dict['tier names']['phoneme'], segments)
    if config_dict['flags']['phone']:
        textgrid.interval_tier_from_array(
            config_dict['tier names']['phone'], segments)

    for entry in table:
        if pronunciation_dict:
            if entry['prompt'] in pronunciation_dict:
                transcription = pronunciation_dict[entry['prompt']]
                print(
                    f"Generating boundaries for {entry['prompt']} which is pronounced {transcription}.")
                entry['transcription'] = transcription

                # Generate an evenly spaced first guess of segmentation by taking the
                # middle third of the potential speech interval and chopping it up.
                earliest_speech = entry['begin'] + .058
                seg_begin = earliest_speech + \
                    (entry['end'] - earliest_speech)*begin_coeff
                seg_end = earliest_speech + \
                    (entry['end'] - earliest_speech)*end_coeff
                boundaries = np.linspace(
                    seg_begin, seg_end, len(transcription) + 3)
                boundaries = boundaries[1:-1]
                entry['segment boundaries'] = boundaries
            else:
                print(
                    f"Word \'{entry['prompt']}\' missing from pronunciation dict.")
        else:
            print(f"Generating boundaries for {entry['prompt']}.")

            earliest_speech = entry['begin'] + .058
            seg_begin = earliest_speech + \
                (entry['end'] - earliest_speech)*begin_coeff
            seg_end = earliest_speech + \
                (entry['end'] - earliest_speech)*end_coeff
            boundaries = [seg_begin, seg_end]
            entry['segment boundaries'] = boundaries


def generate_textgrid(table, filename, config_dict, pronunciation_dict=None) -> None:
    """
    _summary_

    Parameters
    ----------
    table : _type_
        _description_
    filename : _type_
        _description_
    config_dict : _type_
        _description_
    pronunciation_dict : _type_, optional
        _description_, by default None
    """

    textgrid = TextGrid()
    add_tiers_to_textgrid(textgrid, table, config_dict, pronunciation_dict)

    files = []
    words = []
    segments = []
    for entry in table:
        file_segment = {
            'label': entry['filename'],
            'begin': entry['sliceBegin'],
            'end': entry['sliceEnd']}
        files.append(file_segment)

        if 'beep' in entry:
            begin_buffer = {
                'label': '',
                'begin': entry['sliceBegin'],
                'end': entry['beep']
            }
            words.append(begin_buffer)
            segments.append(begin_buffer)

            beep = {
                'label': 'BEEP',
                'begin': entry['beep'],
                'end': entry['beep'] + 0.05
            }
            words.append(beep)
            segments.append(beep)

            after_beep = {
                'label': '',
                'begin': entry['beep'] + 0.05,
                'end': entry['segment boundaries'][0]
            }
            words.append(after_beep)
            segments.append(after_beep)
        else:
            begin_buffer = {
                'label': '',
                'begin': entry['sliceBegin'],
                'end': entry['segment boundaries'][0]
            }
            words.append(begin_buffer)
            segments.append(begin_buffer)

        # For words and utterances one long interval.
        word = {
            'label': entry['prompt'],
            'begin': entry['segment boundaries'][0],
            'end': entry['segment boundaries'][-1]
        }
        words.append(word)

        if pronunciation_dict:
            # For segmentation a bunch of segment intervals
            for i, label in enumerate(entry['transcription']):
                segment = {
                    'label': label,
                    'begin': entry['segment boundaries'][i],
                    'end': entry['segment boundaries'][i+1]
                }
                segments.append(segment)

        end_buffer = {
            'label': '',
            'begin': entry['segment boundaries'][-1],
            'end': entry['sliceEnd']}
        words.append(end_buffer)
        segments.append(end_buffer)

    # After transforming the table into another list of dicts
    # write the timing segmentation info into a .csv file or buffer.
    # Construct a 'Segment' Tier from the .csv and write it out
    # Copy the 'Segment' as 'Phonetic detail' or some such as well.
    # Likewise (actually first), construct Tiers 'Utterance' and 'Word'
    if config_dict['flags']['file']:
        textgrid.interval_tier_from_array("File", files)
    if config_dict['flags']['utterance']:
        textgrid.interval_tier_from_array(
            config_dict['tier names']['utterance'], words)
    if config_dict['flags']['word']:
        textgrid.interval_tier_from_array(
            config_dict['tier names']['word'], words)
    if config_dict['flags']['phoneme']:
        textgrid.interval_tier_from_array(
            config_dict['tier names']['phoneme'], segments)
    if config_dict['flags']['phone']:
        textgrid.interval_tier_from_array(
            config_dict['tier names']['phone'], segments)
    textgrid.write(filename)
