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
from scipy.signal import butter, filtfilt, kaiser, sosfilt
from scikits.audiolab import Sndfile, Format
from subprocess import call

pp = pprint.PrettyPrinter(indent=4)


def high_pass(fs):
    stop = (50/(fs/2)) # 50 Hz stop band    
    b, a = butter(10, stop, 'highpass')
    return(b, a)

def low_pass(fs):
    stop = (2200/(fs/2)) # 50 Hz stop band    
    b, a = butter(10, stop, 'lowpass')
    return(b, a)

# This one uses cascaded second order sections (sos), because the b, a format would be unstable.
def band_pass(fs):
    nyq = 0.5 * fs
    low = 950.0 / nyq
    high = 1050.0 / nyq
    sos = butter(1, [low, high], btype='band', output='sos')
    return(sos)


def plot_signals(beep, beep2, int_time, int_signal, hp_signal, bp_signal, int_signal2):
    fig = plt.figure()
    ax0 = fig.add_subplot(211)
    ax1 = fig.add_subplot(212)
    ax0.plot(int_time, int_signal)
    ax0.plot(int_time, int_signal2)
    y = [-20, -90]
    ax0.plot([beep, beep], y)
    ax0.plot([beep2, beep2], y)
    ax1.plot(int_time, hp_signal)
    ax1.plot(int_time, bp_signal)
    ax1.plot([beep, beep], [-1, 1])
    ax1.plot([beep2, beep2], [-1, 1])
    plt.show()


def beep_detect(frames, fs, b, a, name):
    hp_signal = filtfilt(b, a, frames)
    sos = band_pass(fs)
    bp_signal = sosfilt(sos, frames)
    bp_signal = sosfilt(sos, bp_signal[::-1])[::-1]
    n = len(hp_signal)

    # 1 ms window
    window_length = int(0.001*fs)

    # pad with zeros at both ends
    padded_signal = np.zeros(n + window_length)
    padded_signal[window_length/2 : window_length/2+n] = \
        np.square(hp_signal) # squared already for rms, r&m later
    padded_signal2 = np.zeros(n + window_length)
    padded_signal2[window_length/2 : window_length/2+n] = \
        np.square(bp_signal) # squared already for rms, r&m later
    
    # square windowed samples
    wind_signal = np.zeros((n, window_length)) 
    bp_wind_signal = np.zeros((n, window_length)) 
    for i in range(window_length):
        wind_signal[:,i] = padded_signal[i:i+n]
        bp_wind_signal[:,i] = padded_signal2[i:i+n]

    # kaiser windowed samples
    intensity_window = kaiser(window_length, 20) # copied from praat
    # multiply each window slice with the window 
    wind_signal = np.dot(wind_signal,np.diag(intensity_window)) 
    bp_wind_signal = np.dot(bp_wind_signal,np.diag(intensity_window)) 

    # The signal is already squared, need to only take mean and root.
    int_signal = 10*np.log(np.sqrt(np.mean(wind_signal, 1)))
    bp_int_signal = 10*np.log(np.sqrt(np.mean(bp_wind_signal, 1)))
    
    # Old int_time was used to almost correct the shift caused by windowing. 
    #int_time = np.linspace(0, float(len(hp_signal) + 
    # (window_length%2 - 1)/2.0)/fs, len(int_signal))
    int_time = np.linspace(0, float(len(hp_signal))/fs, len(hp_signal))
    int_signal[int_time < 1] = -80

    # First form a rough estimate of where the beep is by detecting the first 
    # big rise in the band passed signal.
    threshold_bp = .9*max(bp_int_signal) + .1*min(bp_int_signal)
    bp_spike_indeces = np.where(bp_int_signal > threshold_bp)
    bp_beep = int_time[bp_spike_indeces[0]]

    # Search for the actual beep in the area from beginning of the recording to 
    # 25 ms before and after where band passing thinks the beep begins.
    roi_beg = bp_spike_indeces[0][0] - int(0.025*fs)
    roi_end = bp_spike_indeces[0][0] + int(0.025*fs)

    # Then look for the more precise rise in the unfiltered signal.
    # TODO: CHECK IF THIS COULD BE DONE IN THE WAVE FORM.
#    threshold = .9*max(int_signal[0:roi_end]) + .1*min(int_signal[0:roi_end])
#    spike_indeces = np.where(int_signal[0:roi_end] > threshold)
#    beep = int_time[spike_indeces]

    # Find the first properly rising edge in the 50 ms window.
    threshold = .1*min(frames[0:roi_end])
    candidates = np.where(frames[roi_beg:roi_end] < threshold)[0]
    beep_approx_index = roi_beg + candidates[0]
    beep_approx = int_time[beep_approx_index]

    zero_crossings = np.where(np.diff(np.signbit(frames[beep_approx_index:roi_end])))[0]
    beep_index = beep_approx_index + zero_crossings[0] + 1 - int(.001*fs)
    beep = int_time[beep_index]

#    if len(beep) < 1:
#        beep = -1
#        has_speech = False
#    else:
#        beep = beep[0] #+ float(window_length/2)/fs
#        beep_index = spike_indeces[0]
#        beep_index = beep_index[0]

    # check if the energy before the beep begins is less 
    # than the energy after the beep.
    split_point = beep_index + int(.075*fs)
    if len(hp_signal) > split_point:
        ave_energy_pre_beep = np.sum(int_signal[:beep_index])/beep_index
        ave_speech_energy = np.sum(int_signal[split_point:])/(len(int_signal)-split_point)
        has_speech = ave_energy_pre_beep < ave_speech_energy

    else:
        # if the signal is very very short, there is no speech
        has_speech = False

    # Test section
    #plot_signals(beep, bp_beep[0], int_time, int_signal, hp_signal, bp_signal, bp_int_signal)


    # An even fancier version could let the user point to the beep etc.
    # But not necessarily a good idea as it's more likely that the threshold 
    # values just need adjusting in general than for one token.
    if not has_speech:
        print "Token ", name, " did not seem to have any speech in it."
        plot_signals(beep, bp_beep[0], int_time, int_signal, hp_signal, bp_signal, bp_int_signal)
        answer = raw_input("Exclude the token (y/n):")
        if answer == "n":
            print "Warning: Including the token, but there will probably" 
            print "be problems in later processing stages."
            has_speech = True

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
        prompt_files = [os.path.join(dirname, 'meta/') + filename + '.txt'
                       for filename in filenames]

    # Check if there are artic files and if yes, use them to decide which 
    # bits to skip. If no, use existence of .ult files.
    artic_annot_exists = False
    if(len(artic_annot_files) < 1):
        print("Didn't find any articulatory annotation files.") 
        #print("Automatic speech detection is not yet in use, but you will get warnings.")
    else:
        artic_annot_exists = True
        artic_annot_files = [os.path.join(dirname, 'artic_annotations/') + 
                             filename + '.TextGrid'
                             for filename in filenames]
    
    uti_files = [os.path.join(dirname, 'uti/') + 
                             filename + '.ult'
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
            elif not os.path.isfile(uti_files[i]):
                print 'Skipping ', filenames[i], '. Token has no ultrasound data.'
                continue
            elif artic_annot_exists and not os.path.isfile(artic_annot_files[i]):
                print 'Skipping ', filenames[i], '. Token has no articulatory annotation.'
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
                beep, has_speech = beep_detect(frames, fs, b, a, filenames[i])
                table[i]['beep'] = beep
                if not has_speech:
                    print "Warning! Token", infile, "doesn't have speech according to beep_detect." 
                    print "\tBeep:", beep, "Length:", duration

                # give fav the stuff from 50ms after the beep begins
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


