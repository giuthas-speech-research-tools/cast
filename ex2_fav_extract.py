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
        fieldnames = ['id', 'speaker', 'sliceBegin', 'beep', 'begin', 'end', 'word']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        map(writer.writerow, table)

    print("Wrote file " + filename + " for R/Python.")


def writeGrid(grid, element, directory):
    filename = os.path.join(directory, element['id'])+'.TextGrid'
    grid.write(filename)
    #print 'Wrote', filename


def gridFromDict(element):
    grid = TextGrid(name = element['speaker'], 
                    maxTime = element['end']-element['sliceBegin'])

    word = IntervalTier('word', maxTime = grid.maxTime)
    grid.append(word)

    segment = IntervalTier('segment', maxTime = grid.maxTime)
    segment.add(0.0, float(element['beep']), '')
    grid.append(segment)

    return grid


def loadTransRules(filename):
    rules = {}
    with closing(open(filename, 'r')) as rulefile:
        for rule in rulefile:
            rule = rule.strip().split(',')
            rules[rule[0]] = rule[1:]
    return rules


def extractGrids(table, mainGrid):
    grids = map(gridFromDict, table)
    words = mainGrid.pop()
    segments = mainGrid.pop()

    transcriptions = loadTransRules("/Users/jpalo/tyot/vaikkari/source/python/phone_transcription_rules.csv")

    i = 0
    for interval in words:
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
            # advance the counter for only those intervals that contain 
            # segmentation information
            i += 1

    i = 0
    seg_iter = segments.__iter__()
    lastBoundary = 0.0
    for interval in seg_iter:
        if 'sp' not in interval.mark:
            offset = -float(table[i]['sliceBegin'])
            tier = grids[i].getFirst('segment')

#            rule = iter(transcriptions[table[i]['word']])

            interval.move(offset)
            interval.mark = transcriptions[interval.mark][0]
            if interval.minTime > float(table[i]['beep']):
                print "offset: ", -offset, i
                tier.add(float(table[i]['beep']), interval.minTime, 'beep')
            else:
                interval = seg_iter.next()
                while 'sp' not in interval.mark:
                    # advance the segment intervals 
                    # until you find an empty interval
                    try:
                        interval = seg_iter.next()
                    except StopIteration:
                        break
                i += 1
                continue
            if interval.maxTime > tier.maxTime:
                interval.maxTime = tier.maxTime
            lastBoundary = interval.maxTime
            tier.addInterval(interval)

            interval = seg_iter.next()
            while 'sp' not in interval.mark:
                interval.move(offset)
                if interval.maxTime > tier.maxTime:
                    interval.maxTime = tier.maxTime
                interval.mark = transcriptions[interval.mark][0]
                lastBoundary = interval.maxTime
                tier.addInterval(interval)
                try:
                    interval = seg_iter.next()
                except StopIteration:
                    break
            tier.add(lastBoundary, tier.maxTime, "")
            i += 1

    return grids, transcriptions


def main(args):
    outdirectory = args.pop()
    resultsFile = args.pop()
    gridFile = args.pop()

    table = read_results(resultsFile)
    mainGrid = TextGridFromFile(gridFile)
    grids, transcriptions = extractGrids(table, mainGrid)

    dirnames = [outdirectory]*len(grids)
    map(writeGrid, grids, table, dirnames)
    print 'Wrote ', str(len(grids)), ' textgrids.'


if (len(sys.argv) != 4):
    print("\nex2_fav_extract.py")
    print("\tusage: ex2_fav_extract.py fave_output.textgrid previous_results.csv output_dir")
    print("\n\tExtracts single token textgrids from FAVE output textgrid.")
    print("\tReads also analysis results produced by ex2_concat.py.")
    print("\tWrites the extracted textgrids with added beep locations to the specified directory.")
    sys.exit(0)


if (__name__ == '__main__'):
    t = time.time()
    main(sys.argv[1:])
    print 'Elapsed time', (time.time() - t)
