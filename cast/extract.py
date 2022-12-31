import csv
import pprint
import sys
import time
from contextlib import closing
from pathlib import Path

import textgrids

pp = pprint.PrettyPrinter(indent=4)


def read_results(results_file: Path):
    # Read data written by ex2_concat.py from a csv-formated file.
    with closing(open(results_file, 'r')) as csvfile:
        reader = csv.DictReader(csvfile, quoting=csv.QUOTE_NONNUMERIC)
        table = [row for row in reader]

    print("Read file " + results_file + ".")
    return table


def extract_grids(table, long_grid, directory):
    utterances = long_grid.interval_tier_to_array("Utterance")
    words = long_grid.interval_tier_to_array("Word")
    segments = long_grid.interval_tier_to_array("Segments")
    details = long_grid.interval_tier_to_array("Phonetic detail")

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

        textgrid.offset_time(-entry["sliceBegin"])

        filename = Path(directory, entry['id']).with_suffix('.TextGrid')
        textgrid.write(filename)
        i += 1

    return i


def extract_textgrids(
        outdirectory: Path, 
        results_file: Path,
        grid_file: Path
    ):

    table = read_results(results_file)

    long_grid = textgrids.TextGrid(grid_file)
    print(f"Read {grid_file}.")

    i = extract_grids(table, long_grid, outdirectory)
    print(f'Wrote {i} textgrids.')

