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
from scipy.io import loadmat
from scikits.audiolab import Sndfile, Format
from subprocess import call

pp = pprint.PrettyPrinter(indent=4)

    

def write_fav_input(table, filename):
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
        fieldnames = ['id', 'speaker', 'sliceBegin', 'beep', 'begin', 'end', 'word']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames,
                                quoting=csv.QUOTE_NONNUMERIC)

        writer.writeheader()
        map(writer.writerow, table)

    print("Wrote file " + filename + " for R/Python.")


def concatenateWavs(dirname, outfilename, speaker_id):
    wav_files = glob.glob(os.path.join(dirname, '*.wav')) 
    prompt_files = glob.glob(os.path.join(dirname, '*.txt')) 

    # Split first to get rid of the suffix, then to get rid of the path.
    filenames = [filename.split('.')[-2].split('/').pop() 
                 for filename in wav_files]
    
    na_file = os.path.join(dirname, 'na_list.txt')
    if os.path.isfile(na_file):
        na_list = [line.rstrip('\n') for line in open(na_file)]
    else:
        na_list = []
        print("Didn't find na_list.txt. Proceeding anyhow.")

    outwave = outfilename + ".wav"
    outfav = outfilename + ".txt"
    outcsv = outfilename + ".csv"

    # initialise table with the speaker_id and name repeated and other fields empty
    table = [{'id':'n/a', 
              'speaker':speaker_id, 
              'sliceBegin':'n/a',
              'beep':'n/a',
              'begin':'n/a', 
              'end':'n/a', 
              'word':'n/a'} 
             for i in range(len(wav_files))]

    if(len(wav_files) < 1):
        print("Didn't find any sound files to concatanate in \'"+dirname+"\'.")
        exit()

    if(len(prompt_files) < 1):
        print("Didn't find any prompt files.")
        exit()
    else:
        # ensure one to one correspondence between wavs and prompts 
        prompt_files = [os.path.join(dirname, filename) + '.txt'
                       for filename in filenames]
    
    uti_files = [os.path.join(dirname, filename) + '.ult' 
                 for filename in filenames]

    cursor = 0.0
    fs = 0
    channels = 0
    format = Format()
    
    # find params from first file
    with closing(Sndfile(wav_files[0], 'r')) as w:
        fs = w.samplerate
        channels = w.channels
        format = w.format

    with closing(Sndfile(outwave, 'w', format, channels, fs)) as output:
        for (i, infile) in enumerate(wav_files):
            if filenames[i] in na_list:
                print 'Skipping', filenames[i], ': Token is in na_list.txt.'
                continue
            elif not os.path.isfile(uti_files[i]):
                print 'Skipping ', filenames[i], '. Token has no ultrasound data.'
                continue
                
            with closing(open(prompt_files[i], 'r')) as prompt_file:
                line = prompt_file.readline().strip()
                line = " ".join(re.findall("[a-zA-Z]+", line))
                if line == 'water swallow' or line == 'BITE PLANE':
                    print 'Skipping', prompt_files[i], line
                    continue

                table[i]['word'] = line

            with closing(Sndfile(infile, 'r')) as w:
                n_frames = w.nframes
                if fs != w.samplerate:
                    print 'Mismatched sample rates in sound files.'
                    print 'Exiting.'
                    exit()

                duration = n_frames / float(fs)
                frames = w.read_frames(n_frames)
            
                # this rather than full path to avoid upsetting praat/FAV
                table[i]['id'] = filenames[i]

                table[i]['sliceBegin'] = cursor

                # give fav the stuff from 1.5s after the audio recording begins
                table[i]['begin'] = cursor + 1.5 

                cursor += duration
                table[i]['end'] = round(cursor, 3)

                output.write_frames(frames)

    # Weed out the skipped ones before writing the data out.
    table = [token for token in table if token['id'] != 'n/a']
    write_fav_input(table, outfav)
    write_results(table, outcsv)
    #pp.pprint(table)


def main(args):
    outfilename = args.pop()
    dirname = args.pop()
    speaker_id = args.pop()
    concatenateWavs(dirname, outfilename, speaker_id)


if (len(sys.argv) != 4):
    print("\nex1_concat.py")
    print("\tusage: ex1_concat.py speaker_id directory outputfilename")
    print("\n\tConcatenates wav files from AAA.")
    print("\tWrites a huge wav-file and a .txt for potential input to FAVE.")
    print("\tAlso writes a richer metafile to be read by ex1_extract.py or similar.")
    sys.exit(0)


if (__name__ == '__main__'):
    t = time.time()
    main(sys.argv[1:])
    print 'Elapsed time', (time.time() - t)


