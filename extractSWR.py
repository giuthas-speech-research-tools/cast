from contextlib import closing
import csv
import os
import pprint
import sys
import time

import textgrids

pp = pprint.PrettyPrinter(indent=4)


def read_results(filename):
    # Read data written by ex2_concat.py from a csv-formated file.
    with closing(open(filename, 'r')) as csvfile:
        reader = csv.DictReader(csvfile, quoting=csv.QUOTE_NONNUMERIC)
        table = [row for row in reader]

    print("Read file " + filename + ".")
    return table


def extractGrids(table, mainGrid, directory):
    utterances = mainGrid.interval_tier_to_array("Utterance")
    words = mainGrid.interval_tier_to_array("Word")
    segments = mainGrid.interval_tier_to_array("Segments")
    details = mainGrid.interval_tier_to_array("Phonetic detail")

    i = 0
    for entry in table:
        utterance = []
        word = []
        segment = []
        detail = []

        for interval in utterances:
            if interval['begin'] >= entry["sliceBegin"] and interval['end'] <= entry["sliceEnd"]:
                utterance.append(interval)
 
        for interval in words:
            if interval['begin'] >= entry["sliceBegin"] and interval['end'] <= entry["sliceEnd"]:
                word.append(interval)
 
        for interval in segments:
            if interval['begin'] >= entry["sliceBegin"] and interval['end'] <= entry["sliceEnd"]:
                segment.append(interval)
  
        for interval in details:
            if interval['begin'] >= entry["sliceBegin"] and interval['end'] <= entry["sliceEnd"]:
                detail.append(interval)

        textgrid = textgrids.TextGrid(xmin = entry["sliceBegin"])
        textgrid.interval_tier_from_array("utterance", utterance)
        textgrid.interval_tier_from_array("word", word)
        textgrid.interval_tier_from_array("segment", segment)
        textgrid.interval_tier_from_array("Phonetic detail", detail)

        textgrid.move_t0(-entry["sliceBegin"])

        filename = os.path.join(directory, entry['id'])+'.TextGrid'
        textgrid.write(filename)
        i += 1

    return i


def main(args):
    outdirectory = args.pop()
    resultsFile = args.pop()
    gridFile = args.pop()

    table = read_results(resultsFile)

    mainGrid = textgrids.TextGrid(gridFile)
    print(f"Read {gridFile}.")

    i = extractGrids(table, mainGrid, outdirectory)
    print(f'Wrote {i} textgrids.')


if (len(sys.argv) != 4):
    print("\nextractSWR.py")
    print("\tusage: extractSWR.py concatenated.textgrid previous_results.csv output_dir")
    print("\n\tExtracts single token textgrids from a concatenated textgrid produced by FAVE or concatenateSWR.py.")
    print("\tReads also analysis results produced by concatenateSWR.py.")
    print("\tWrites the extracted textgrids to the specified directory.")
    sys.exit(0)


if (__name__ == '__main__'):
    t = time.time()
    main(sys.argv[1:])
    print('Elapsed time %f.', (time.time() - t))
