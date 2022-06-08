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
from scipy.signal import butter, filtfilt, kaiser
from scikits.audiolab import Sndfile, Format

pp = pprint.PrettyPrinter(indent=4)


def high_pass(fs):
    stop = (50/(fs/2)) # 50 Hz stop band    
    b, a = butter(10, stop, 'highpass')
    return(b, a)


def low_pass(fs):
    stop = (2200/(fs/2)) # 50 Hz stop band    
    b, a = butter(10, stop, 'lowpass')
    return(b, a)

# something deeply wrong with this as it flattens the whole signal.
def band_pass(fs):
    nyq = 0.5 * fs
    low = 50.0 / nyq
    high = 2200.0 / nyq
    b, a = butter(10, [low, high], btype='band')
#    passband = [50/(fs/2), 2200/(fs/2)]
#    b, a = butter(10, passband, btype='band')
    return(b, a)


def plot_signals(beep, int_time, int_signal, hp_signal):
    fig = plt.figure()
    ax0 = fig.add_subplot(211)
    ax1 = fig.add_subplot(212)
    ax0.plot(int_time, int_signal)
    y = [-20, -90]
    ax0.plot([beep, beep], y)
    ax1.plot(int_time, hp_signal)
    ax1.plot([beep, beep], [-1, 1])
    plt.show()


def beep_detect(frames, fs, b, a):
    hp_signal = filtfilt(b, a, frames)
    n = len(hp_signal)

    # 1 ms window
    window_length = int(0.001*fs)

    # pad with zeros at both ends
    padded_signal = np.zeros(n + window_length)
    padded_signal[window_length/2 : window_length/2+n] = \
        np.square(hp_signal) # squared already for rms, r&m later
    
    # square windowed samples
    wind_signal = np.zeros((n, window_length)) 
    for i in range(window_length):
        wind_signal[:,i] = padded_signal[i:i+n]

    # kaiser windowed samples
    intensity_window = kaiser(window_length, 20) # copied from praat
    # multiply each window slice with the window 
    wind_signal = np.dot(wind_signal,np.diag(intensity_window)) 

    # The signal is already squared, need to only take mean and root.
    int_signal = 10*np.log(np.sqrt(np.mean(wind_signal, 1)))
    
    # Old int_time was used to almost correct the shift caused by windowing. 
    #int_time = np.linspace(0, float(len(hp_signal) + 
    # (window_length%2 - 1)/2.0)/fs, len(int_signal))
    int_time = np.linspace(0, float(len(hp_signal))/fs, len(hp_signal))
    int_min = min(int_signal)
    int_max = max(int_signal)
    int_threshold = .4*int_min + .6*int_max
    int_signal[int_time < 1] = int_min #-80


    # this is frustratingly almost right, triggers just a tad too soon
    spike_indeces = np.where(int_signal > int_threshold) # -50
    beep = int_time[spike_indeces]
    if len(beep) < 1:
        beep = -1
        has_speech = False
    else:
        beep = beep[0] #+ float(window_length/2)/fs
        beep_index = spike_indeces[0]
        beep_index = beep_index[0]

        # check if the energy up to 75 ms after the beep begins is less 
        # than the energy after that point.
        split_point = beep_index + int(.05*fs)
        if len(hp_signal) > split_point:
            speech = np.where(int_signal[split_point:] > int_threshold)
            has_speech = len(speech) > 0
        else:
            # if the signal is very very short, there is no speech
            has_speech = False

    return (beep, has_speech)
    

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
    wav_files = glob.glob(os.path.join(dirname, 'sound/*.wav')) 
    prompt_files = glob.glob(os.path.join(dirname, 'meta/*.txt')) 
    artic_annot_files = glob.glob(os.path.join(dirname, 'artic_annotations/*.TextGrid')) 

    # Split first to get rid of the suffix, then to get rid of the path.
    filenames = [filename.split('.')[-2].split('/').pop() 
                 for filename in wav_files]
    
    na_file = os.path.join(dirname, 'na_list.txt')
    if os.path.isfile(na_file):
        na_list = [line.rstrip('\n') for line in open()]
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
        print("Didn't find any sound files to concatanate in "+dirname+".")
        exit()

    if(len(prompt_files) < 1):
        print("Didn't find any prompt files.")
        exit()
    else:
        # ensure one to one correspondence between wavs and prompts 
        prompt_files = [os.path.join(dirname, 'meta/') + filename + '.txt'
                       for filename in filenames]

    if(len(artic_annot_files) < 1):
        print("Didn't find any articulatory annotation files.") 
        print("Automatic speech detection is not yet in use, but you will get warnings.")
    else:
        artic_annot_files = [os.path.join(dirname, 'artic_annotations/') + 
                             filename + '.TextGrid'
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
        b, a = high_pass(fs)
        for (i, infile) in enumerate(wav_files):
            if filenames[i] in na_list:
                print 'Skipping', filenames[i], ': Token is in na_list.txt.'
                continue
            elif not os.path.isfile(artic_annot_files[i]):
                print 'Skipping', filenames[i], '. Token has no articulatory annotation.'
                continue
                
            with closing(open(prompt_files[i], 'r')) as prompt_file:
                line = prompt_file.readline().strip()
                line = " ".join(re.findall("[a-zA-Z]+", line))
                if line == 'water swallow' or line == 'bite plate':
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
            
                # print infile, n_frames

                # this rather than full path to avoid upsetting praat/FAV
                table[i]['id'] = filenames[i]

                table[i]['sliceBegin'] = cursor
                beep, has_speech = beep_detect(frames, fs, b, a)
                table[i]['beep'] = beep
                if not has_speech:
                    print "Warning! Token", infile, "doesn't have speech according to beep_detect."

                # give fav the stuff from 50ms after the beep
                table[i]['begin'] = cursor + table[i]['beep'] + 0.05 

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
    print("\nex2_concat.py")
    print("\tusage: ex2_concat.py speaker_id directory outputfilename")
    print("\n\tConcatenates wav files from AAA and finds the stimulus beep.")
    print("\tWrites a huge wav-file and a .txt for input to FAVE.")
    print("\tAlso writes a richer metafile to be read by ex2_fav_extract.py or similar.")
    sys.exit(0)


if (__name__ == '__main__'):
    t = time.time()
    main(sys.argv[1:])
    print 'Elapsed time', (time.time() - t)


