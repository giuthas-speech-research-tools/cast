from contextlib import closing
import glob
import os
from pathlib import Path
import pprint
import sys
from typing import Tuple, Union

import numpy as np

# wav file handling
import scipy.io.wavfile as sio_wavfile

import textgrids

import cast.audio_processing as audio_processing

from cast.config_file_io import read_exclusion_list
from cast.csv_output import write_results
from cast.aaa_meta import check_and_load_aaa_meta
from cast.rasl_meta import check_and_load_rasl_meta

pp = pprint.PrettyPrinter(indent=4)

def add_boundaries_and_segments(table, config_dict, pronunciation_dict=None) -> None:
    begin_coeff = config_dict['word guess']['begin']
    end_coeff = config_dict['word guess']['end']
    for entry in table:
        if pronunciation_dict:
            if entry['word'] in pronunciation_dict:
                transcription = pronunciation_dict[entry['word']]
                print(f"Generating boundaries for {entry['word']} which is pronounced {transcription}.")
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
                print(f"Word \'{entry['word']}\' missing from pronunciation dict.")
        else:
            print(f"Generating boundaries for {entry['word']}.")

            earliest_speech = entry['begin'] +.058
            seg_begin = earliest_speech + (entry['end'] - earliest_speech)*begin_coeff
            seg_end = earliest_speech + (entry['end'] - earliest_speech)*end_coeff
            boundaries = [seg_begin, seg_end]
            entry['segment boundaries'] = boundaries    


def generate_textgrid(table, filename, config_dict, pronunciation_dict=None) -> None:

    add_boundaries_and_segments(table, config_dict, pronunciation_dict)

    textgrid = textgrids.TextGrid()
    words = []
    segments = []
    for entry in table:
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
            'label': entry['word'], 
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
    textgrid.interval_tier_from_array("Utterance", words)
    textgrid.interval_tier_from_array("Word", words)
    if pronunciation_dict:
        textgrid.interval_tier_from_array("Phoneme", segments)
        textgrid.interval_tier_from_array("Phone", segments)
    textgrid.write(filename)


def process_wav_file(table_entry, samplerate, number_of_channels, cursor, 
                    filter=None) -> Tuple[float, np.ndarray]:
    (next_samplerate, frames) = sio_wavfile.read(table_entry['wav_file'])
    n_frames = frames.shape[0]
    if len(frames.shape) == 1:
        n_channels = 1
    else:
        n_channels = frames.shape[1]

    if next_samplerate != samplerate:
        print('Mismatched sample rates in sound files.')
        print("{next_samplerate} in {infile} is not the common one: {samplerate}".format(
            next_samplerate=next_samplerate, infile=table_entry['wav_file'], 
            samplerate=samplerate))
        print('Exiting.')
        sys.exit()

    if n_channels != number_of_channels:
        print('Mismatched numbers of channels in sound files.')
        print("{n_channels} in {infile} is not the common one: {number_of_channels}".format(
            n_channels=n_channels, infile=table_entry['wav_file'], 
            number_of_channels=number_of_channels))
        print('Exiting.')
        sys.exit()

    duration = n_frames / float(samplerate)

    table_entry['sliceBegin'] = cursor

    # setup the high-pass filter for removing the mains frequency (and anything below it)
    # from the recorded sound.
    if filter:
        beep, has_speech = audio_processing.detect_beep_and_speech(
            frames, samplerate,filter['b'], filter['a'], table_entry['filename'])
        table_entry['beep'] = cursor + beep
        table_entry['has speech'] = has_speech

    # Start segmentation in FAV and other systems after the beep.
    if filter:
        table_entry['begin'] = cursor + beep + 0.05
    else: 
        table_entry['begin'] = cursor
    cursor += duration
    table_entry['end'] = round(cursor, 3)
    table_entry['sliceEnd'] = cursor

    return cursor, frames

def apply_exclusion_list(table: list[dict], exclusion_path: Path) -> None:

    exclusion_list = read_exclusion_list(exclusion_path)

    for entry in table:
        filename = entry['filename']
        if filename in exclusion_list['files']:
            print(f'Excluding {filename}: File is in exclusion list.')
            entry['excluded'] = True

        # The first condition sees if the whole prompt is excluded, 
        # the second condition checks if any parts of the prompt 
        # match exclucion criteria (for example excluding 'foobar ...' 
        # based on 'foobar').
        prompt = entry['prompt']
        if (prompt in exclusion_list['prompts'] or
            [element for element in exclusion_list['parts of prompts'] if(element in prompt)]):
            print(f'Excluding {filename}. Prompt: {prompt} matches exclusion list.')
            entry['excluded'] = True



def concatenate_wavs(speaker_id: str, directory: Union[str, Path], 
                        outputfile: Union[str, Path], config_dict: dict, 
                        pronunciation_dict: dict=None, 
                        test: bool=False, detect_beep: bool=False, only_words: bool=False):
    if isinstance(directory, str):
        directory = Path(directory)
    if isinstance(outputfile, str):
        outputfile = Path(outputfile)

    data_source = config_dict['data source']
    if data_source == 'AAA':
        check_and_load_aaa_meta(speaker_id, directory, test)
    elif data_source == 'RASL':
        check_and_load_rasl_meta(speaker_id, directory, test)
    else:
        print(f"Unknown data source: {data_source}. Exiting.")
        sys.exit()

    apply_exclusion_list(table, Path(config_dict['exclusion list']))

    # Only add the beep entry if we are going to be using it.
    if detect_beep:
        for entry in table:
            entry['beep'] = 'n/a' 

    outwave = outputfile + ".wav"
    outcsv = outputfile + ".csv"
    out_textgrid = outputfile + ".TextGrid"
    
    # find params from first file
    samplerate, test_data = sio_wavfile.read(table[0]['wav_path'])
    if len(test_data.shape) == 1:
        number_of_channels = 1
    else:
        number_of_channels = test_data.shape[1]

    # Read wavs and keep track of file boundaries.
    # TODO: consider moving the whole loop into processWavFile and renaming the function
    if detect_beep:
        mainsFrequency = 60
        filter = audio_processing.high_pass(samplerate, mainsFrequency)

    cursor = 0.0
    frames = None
    for entry in table:
        if entry['excluded']:
            continue
        if detect_beep:
            cursor, new_frames = process_wav_file(entry, samplerate, 
                    number_of_channels, cursor, filter=filter)
        else:
            cursor, new_frames = process_wav_file(entry, samplerate, 
                    number_of_channels, cursor)
        if new_frames is None:
            continue
        if frames is None:
            frames = new_frames
        else:
            frames = np.concatenate([frames, new_frames], axis = 0)

    # Write the concatanated wav.
    with closing(open(outwave, 'wb')) as output:
        sio_wavfile.write(output, samplerate, frames)

    # Weed out the skipped ones before writing the data out.
    table = [token for token in table if token['id'] != 'n/a']
    write_results(table, outcsv)
    if only_words:
        generate_textgrid(table, out_textgrid, config_dict)
    else:
        generate_textgrid(table, out_textgrid, config_dict, pronunciation_dict)
    # pp.pprint(table)

