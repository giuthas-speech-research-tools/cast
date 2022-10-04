from contextlib import closing
import glob
import os
import pprint
import sys
import time

import numpy as np

# wav file handling
import scipy.io.wavfile as sio_wavfile

import textgrids

import audio_processing

from cast.config_file_io import read_na_list
from cast.csv_output import write_results

pp = pprint.PrettyPrinter(indent=4)

def write_concatenated_textgrid(table, filename, pronunciation_dict_name):

    for entry in table:
        print("Processing {word}.".format(
            word = entry['word']))

        # Generate an evenly spaced first guess of segmentation by taking the 
        # middle third of the potential speech interval and chopping it up. 
        earliest_speech = entry['begin'] +.058
        seg_begin = earliest_speech + (entry['end'] - earliest_speech)/12
        seg_end = earliest_speech + (entry['end'] - earliest_speech)*2/3

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
                'label': '', 
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
    textgrid.interval_tier_from_array("Segments", segments)
    textgrid.interval_tier_from_array("Phonetic detail", segments)
    textgrid.write(filename)


def process_wav_file(table_entry, wav_file, filename, prompt_file, uti_file, 
                    na_list, samplerate, number_of_channels, cursor, 
                    filter=None, detect_beep=False):
    if filename in na_list:
        print('Skipping {filename}: Recording is in na_list.txt.'.format(filename=filename))
        return cursor, None
    elif not os.path.isfile(uti_file):
        print ('Skipping {filename}. Recording has no ultrasound data.'.format(filename=filename))
        return cursor, None
        
    with closing(open(prompt_file, 'r')) as prompt_file:
        line = prompt_file.readline().strip()
        #line = " ".join(re.findall("[a-zA-Z]+", line))
        if 'tap test' in line or 'water swallow' in line or 'biteplate' in line:
            print('Skipping {file} is a {prompt}'.format(file=prompt_file, prompt=line))
            return cursor, None

        table_entry['word'] = line

    (next_samplerate, frames) = sio_wavfile.read(wav_file)
    n_frames = frames.shape[0]
    if len(frames.shape) == 1:
        n_channels = 1
    else:
        n_channels = frames.shape[1]

    if next_samplerate != samplerate:
        print('Mismatched sample rates in sound files.')
        print("{next_samplerate} in {infile} is not the common one: {samplerate}".format(
            next_samplerate=next_samplerate, infile=wav_file, samplerate=samplerate))
        print('Exiting.')
        sys.exit()

    if n_channels != number_of_channels:
        print('Mismatched numbers of channels in sound files.')
        print("{n_channels} in {infile} is not the common one: {number_of_channels}".format( 
            n_channels=n_channels, infile=wav_file, number_of_channels=number_of_channels))
        print('Exiting.')
        sys.exit()

    duration = n_frames / float(samplerate)

    # this rather than full path to avoid upsetting praat/FAV
    table_entry['id'] = filename

    table_entry['sliceBegin'] = cursor

    # setup the high-pass filter for removing the mains frequency (and anything below it)
    # from the recorded sound.
    if detect_beep:
        beep, has_speech = audio_processing.detect_beep_and_speech(
            frames, samplerate,filter['b'], filter['a'], filename)
        table_entry['beep'] = cursor + beep
        table_entry['has speech'] = has_speech

    # Start segmentation in FAV and other systems after the beep.
    if detect_beep:
        table_entry['begin'] = cursor + beep + 0.05
    else: 
        table_entry['begin'] = cursor
    cursor += duration
    table_entry['end'] = round(cursor, 3)
    table_entry['sliceEnd'] = cursor

    return cursor, frames


def concatenate_wavs(speaker_id, dirname, outfilename, test = False, detect_beep = False):
    wav_files = sorted(glob.glob(os.path.join(dirname, '*.wav')))
    # for test runs do only first ten files:
    if test:
        wav_files = wav_files[:10]

    if(len(wav_files) < 1):
        print("Didn't find any sound files to concatanate in \'{dirname}\'.".format(dirname))
        exit()

    # Split first to get rid of the suffix, then to get rid of the path.
    filenames = [filename.split('.')[-2].split('/').pop() 
                 for filename in wav_files]

    # initialise table with the speaker_id and name repeated, wav_file name
    # from the list, and other fields empty
    table = [{
                'wav_path': wavfile,
                'id':'n/a',
                'speaker':speaker_id, 
                'sliceBegin':'n/a',
                'beep':'n/a',
                'begin':'n/a', 
                'end':'n/a', 
                'word':'n/a'} 
             for i, wavfile in  enumerate(wav_files)]

    prompt_files = sorted(glob.glob(os.path.join(dirname, '*.txt'))) 

    if(len(prompt_files) < 1):
        print("Didn't find any prompt files.")
        exit()
    else:
        # ensure one to one correspondence between wavs and prompts 
        prompt_files = [os.path.join(dirname, filename) + '.txt'
                       for filename in filenames]

    na_list = read_na_list(dirname)

    outwave = outfilename + ".wav"
    outcsv = outfilename + ".csv"
    out_textgrid = outfilename + ".TextGrid"
    
    uti_files = [os.path.join(dirname, filename) + '.ult' 
                 for filename in filenames]
    
    # find params from first file
    samplerate, test_data = sio_wavfile.read(wav_files[0])
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
    for i in range(len(wav_files)):
        print(wav_files[i])
        if detect_beep:
            cursor, new_frames = process_wav_file(table[i], wav_files[i], filenames[i], 
                    prompt_files[i], uti_files[i], 
                    na_list, samplerate, number_of_channels, cursor, filter)
        else:
            cursor, new_frames = process_wav_file(table[i], wav_files[i], filenames[i], 
                    prompt_files[i], uti_files[i], 
                    na_list, samplerate, number_of_channels, cursor)
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
    #pp.pprint(table)


def main(args):
    outfilename = args.pop()
    original_dirname = args.pop()
    speaker_id = args.pop()
    if args:
        if '--test' in args:
            test = True
        else:
            test = False
        if '--beep' in args:
            detect_beep = True
        else:
            detect_beep = False
        concatenate_wavs(speaker_id, original_dirname, outfilename, 
            test = test, detect_beep = detect_beep)
    else: 
        concatenate_wavs(speaker_id, original_dirname, 
            outfilename)


if (len(sys.argv) not in [5, 6]):
    print("\nconcatenate.py")
    print("\tusage: concatenate.py [--test] [--beep] speaker_id original_directory pronunciation_dict_name outputfilename")
    print("\n\tConcatenates wav files and creates a corresponding TextGrid.")
    print("\t--test runs the code on only first ten files")
    print("\t--beep finds a 1kHz 50ms beep (go-signal), marks it, and starts segmentation after it.")
    print("\tWrites a huge wav-file.")
    print("\tAlso writes a richer metafile to be read by extract.py or similar.")
    print("\tAlso writes a huge textgrid with phonological transcriptions of the words.")
    sys.exit(0)


if (__name__ == '__main__'):
    t = time.time()
    main(sys.argv[1:])
    print('Elapsed time {elapsed_time}'.format(elapsed_time = (time.time() - t)))


