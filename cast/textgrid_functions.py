import pprint
import sys
from contextlib import closing
from pathlib import Path
from typing import Tuple, Union

import numpy as np
import textgrids

pp = pprint.PrettyPrinter(indent=4)

# def add_boundaries_and_segments:


def generate_boundaries_and_segments(table, config_dict, pronunciation_dict=None) -> None:
    begin_coeff = config_dict['word guess']['begin']
    end_coeff = config_dict['word guess']['end']

    if config_dict['flags']['utterance'] or config_dict['flags']['word']:
        textgrid.interval_tier_from_array(config_dict['tier names']['word'], words)
    if config_dict['flags']['phoneme']:
        textgrid.interval_tier_from_array(config_dict['tier names']['phoneme'], segments)
    if config_dict['flags']['phone']:
        textgrid.interval_tier_from_array(config_dict['tier names']['phone'], segments)

    for entry in table:
        if pronunciation_dict:
            if entry['prompt'] in pronunciation_dict:
                transcription = pronunciation_dict[entry['prompt']]
                print(f"Generating boundaries for {entry['prompt']} which is pronounced {transcription}.")
                entry['transcription'] = transcription

                # Generate an evenly spaced first guess of segmentation by taking the 
                # middle third of the potential speech interval and chopping it up. 
                earliest_speech = entry['begin'] +.058
                seg_begin = earliest_speech + (entry['end'] - earliest_speech)*begin_coeff
                seg_end = earliest_speech + (entry['end'] - earliest_speech)*end_coeff
                boundaries = np.linspace(seg_begin, seg_end, len(transcription) + 3)
                boundaries = boundaries[1:-1]
                entry['segment boundaries'] = boundaries
            else:
                print(f"Word \'{entry['prompt']}\' missing from pronunciation dict.")
        else:
            print(f"Generating boundaries for {entry['prompt']}.")

            earliest_speech = entry['begin'] +.058
            seg_begin = earliest_speech + (entry['end'] - earliest_speech)*begin_coeff
            seg_end = earliest_speech + (entry['end'] - earliest_speech)*end_coeff
            boundaries = [seg_begin, seg_end]
            entry['segment boundaries'] = boundaries    


def generate_textgrid(table, filename, config_dict, pronunciation_dict=None) -> None:

    generate_boundaries_and_segments(table, config_dict, pronunciation_dict)

    textgrid = textgrids.TextGrid()
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
        textgrid.interval_tier_from_array(config_dict['tier names']['utterance'], words)
    if config_dict['flags']['word']:
        textgrid.interval_tier_from_array(config_dict['tier names']['word'], words)
    if config_dict['flags']['phoneme']:
        textgrid.interval_tier_from_array(config_dict['tier names']['phoneme'], segments)
    if config_dict['flags']['phone']:
        textgrid.interval_tier_from_array(config_dict['tier names']['phone'], segments)
    textgrid.write(filename)
