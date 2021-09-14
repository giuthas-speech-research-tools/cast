from contextlib import closing
import csv
import glob
import os
import pprint
import re
import sys
import wave
import time
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import loadmat
from scipy.signal import butter, filtfilt, kaiser
from scikits.audiolab import Sndfile, Format
from textgrid import *

pp = pprint.PrettyPrinter(indent=4)


def read_results(filename):
    # Read data written by ex2_concat.py from a csv-formated file.
    with closing(open(filename, 'r')) as csvfile:
        reader = csv.DictReader(csvfile, quoting=csv.QUOTE_NONNUMERIC)
        table = [row for row in reader]

    print("Read file " + filename + ".")
    return table


def write_results(table, filename):
    # Dump all the metadata into a csv-formated file to
    # be read by Python or R.
    with closing(open(filename, 'w')) as csvfile:
        fieldnames = ['id', 'speaker', 'sliceBegin', 'beep', 'begin', 'end', 'word', 'raw_acRT', 'acRT']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        map(writer.writerow, table)

    print("Wrote file " + filename + " for R/Python.")


def foobar(interval, tier, table, grids):
    if interval.mark != 'sp':
        interval.mark = interval.mark.lower()
        interval.move(-float(table[i]['sliceBegin']))       
        tier = grids[i].getFirst('word')
        
        if interval.minTime > tier.maxTime:
            print "Segmentation error:", interval
        elif interval.maxTime > tier.maxTime:
            print "Warning word interval exceeds recording length."
            print "\tRecording length:", tier.maxTime 
            print "\tInterval:", interval
            tier.add(interval.minTime, tier.maxTime, interval.mark)
        else: 
            tier.addInterval(interval)
            tier.add(interval.maxTime, tier.maxTime, "")


def extractGrids(table, mainGrid):
    onsets = mainGrid.pop()

    for token in table:
        token['raw_acRT'] = 0
        token['acRT'] = 0

    i = 0
    for interval in onsets:
        while interval.maxTime > table[i]['end']:
            i += 1
            
            if i >= len(table):
                break # get rid of the last interval since that is not data, just end of file.

        if i < len(table):
            table[i]['raw_acRT'] = interval.maxTime
            table[i]['acRT'] = interval.maxTime - table[i]['sliceBegin']

    return table


def main(args):
    outfilename = args.pop()
    previous_resultsFile = args.pop()
    gridFile = args.pop()

    table = read_results(previous_resultsFile)
    mainGrid = TextGridFromFile(gridFile)
    table = extractGrids(table, mainGrid)

    write_results(table, outfilename)
    print 'Wrote ', outfilename, '.'


if (len(sys.argv) != 4):
    print("\nex1_praat_extract.py")
    print("\tusage: ex1_praat_extract.py onsets.textgrid previous_results.csv output_file")
    print("\n\tExtracts acoustic onset times from a monolithic textgrid.")
    print("\tReads also analysis results produced by ex1_concat.py.")
    print("\tWrites a .csv updated with acoustic onset times.")
    sys.exit(0)


if (__name__ == '__main__'):
    t = time.time()
    main(sys.argv[1:])
    print 'Elapsed time', (time.time() - t)
