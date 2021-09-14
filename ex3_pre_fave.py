from contextlib import closing
import csv
import glob
import os
import pprint
import re
import wave
import sys
import time
import numpy as np
import matplotlib.pyplot as plt
from itertools import groupby
from scipy.io import loadmat
from scikits.audiolab import Sndfile, Format
from subprocess import call

pp = pprint.PrettyPrinter(indent=4)


def find_beeps(filename, speaker_id):
    with closing(Sndfile(filename, 'r')) as wave:
        n_frames = wave.nframes
        fs = wave.samplerate
        duration = n_frames / float(fs)
        frames = wave.read_frames(n_frames)

        spike_indeces = np.where(frames > .9*max(frames))[0]
        zero_indeces = np.where(np.diff(np.signbit(frames)))[0]

        beep_begs = []
        while len(spike_indeces) > .01*fs:
            # find zerocrossing after the first spike
            zero_indeces = zero_indeces[np.where(zero_indeces > spike_indeces[0])]

            # backtrack one half wave
            beep_index = zero_indeces[0] - .0005*fs
            beep_begs.append(beep_index/fs)
            
            # skip ahead enough to properly be clear of the current beep
            spike_indeces = spike_indeces[np.where(spike_indeces > (beep_index + .5*fs))]

        table = [{'id': filename, 
                  'speaker': speaker_id, 
                  'begin': beep_begs[i],
                  'end': beep_begs[i] + .1, 
                  'word': 'beep'} 
                 for i in range(len(beep_begs))]

        print 'Found ' + str(len(table)) + ' beeps in ' + filename

    return (table, duration)


def add_tokens(word_list, table, file_length):
    # The basic premise is that first recordings may be misfires. 
    # This is only a guess and has to be checked in the actual audio.
    offset = len(table) - len(word_list)
    if offset < 0:
        offset = 0
        # In this data set this works. In others, it will not.
        word_list = word_list[1:]
        print "Warning: In this data set this works. In others, it will not."
        print "\tword_list = word_list[1:]"

    ends = [token['begin'] for token in table]
    ends.append(file_length)
    ends = ends[-len(word_list):]

    token_table = [
        {'id': table[i+offset]['id'], 
         'speaker': table[i+offset]['speaker'], 
         'begin': table[i+offset]['end'], 
         'end': ends[i], 
         'word': word_list[i]}
        for i in range(len(word_list))]

    for i in reversed(range(len(token_table))):
        table.insert(i+offset+1, token_table[i])        

    print 'Added ' + str(len(word_list)) + ' tokens.'

    return table


def write_fav_input(table, filename):

    table = [token for token in table if token['word'] != 'beep']
    table = [token for token in table if token['word'] != '']

    # Finally dump all the metadata into a csv-formated file to
    # be read by FAVE.
    with closing(open(filename, 'w')) as csvfile:
        fieldnames = ['id', 'speaker', 'begin', 'end', 'word']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, 
                                delimiter='\t', quoting=csv.QUOTE_NONE,
                                extrasaction='ignore')

        map(writer.writerow, table)

    print("Wrote file " + filename + " for FAVE align.")


def write_results(table, filename):
    # Finally dump all the metadata into a csv-formated file to
    # be read by Python or R.
    with closing(open(filename, 'w')) as csvfile:
        fieldnames = ['id', 'speaker', 'begin', 'end', 'word']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, 
                                delimiter='\t', quoting=csv.QUOTE_NONE,
                                extrasaction='ignore')

        writer.writeheader()
        map(writer.writerow, table)

    print("Wrote file " + filename + " for R/Python.")


def read_token_table():
    filename = "Pertti4/silppulogi.csv"
    with closing(open(filename, 'r')) as csvfile:
        reader = csv.DictReader(csvfile, quoting=csv.QUOTE_NONE)
        table = [row for row in reader]

    beep_file = ''
    hifi_file = ''
    for token in table:
        if token['beep_file'] == '':
            token['beep_file'] = beep_file
            token['hifi_file'] = hifi_file
        else:
            beep_file = token['beep_file']
            hifi_file = token['hifi_file']

    print("Read file " + filename + ".")

    return table


def main(args):
    outputsuffix = args.pop()

    full_list = read_token_table()

    fav_input_files = []

    for speaker_id, participants_token_grouper in groupby(full_list, lambda token: token['id']):
        dirname = 'pertti4/pertti2-' + speaker_id.replace('_', '-') + '/hifi'
        participants_token_list = list(participants_token_grouper)

        for filename, token_grouper in groupby(participants_token_list, lambda token: token['beep_file']):
            filename = os.path.join(dirname, filename) 
            (table, duration) = find_beeps(filename, speaker_id)

            token_list = list(token_grouper)
            prompt_list = [token['prompt'] for token in token_list]
            table = add_tokens(prompt_list, table, duration)

            fave_input = filename.split('.')[-2] + outputsuffix
            write_fav_input(table, fave_input)
            write_results(table, filename.split('.')[-2] + '.csv')

            hifi_file = token_list[0]['hifi_file']
            speech_filename = os.path.join(dirname, hifi_file)
            fav_input_files.append((speech_filename, fave_input))
            
    with closing(open('ex3_fave_commands', 'w')) as fave_batch:
        for (wavfile, inputfile) in fav_input_files:
            fave_batch.write('python FAAValign.py -d ex3/fave_dictionary' +
                             ' \"ex3/' + wavfile +
                             '\" \"ex3/' + inputfile +
                             '\" \"ex3/' + inputfile.split('.')[-2] + '.TextGrid' +
                             '\"\n')


if (len(sys.argv) != 2):
    print("\nex3_pre_fave.py")
    print("\tusage: ex3_pre_fave.py outputsuffix")
    print("\n\tPreprocessing script to be run before fave.")
    print("\n\tReads silppulogi.csv and process all participants in one go.")
    print("\n\tWrites fave input files and fave commands.")
    print("\tAlso writes a richer metafile to be read by ex3_fav_extract.py.")
    sys.exit(0)


if (__name__ == '__main__'):
    t = time.time()
    main(sys.argv[1:])
    print 'Elapsed time', (time.time() - t)


