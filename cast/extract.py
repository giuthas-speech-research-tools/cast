import csv
import pprint
from contextlib import closing
from pathlib import Path
from typing import Dict, List

from textgrids import TextGrid

pp = pprint.PrettyPrinter(indent=4)


def read_results_csv(results_file: Path):
    """Read data written by cast concatenate from a csv-formated file."""
    with closing(open(results_file, 'r')) as csvfile:
        reader = csv.DictReader(csvfile, quoting=csv.QUOTE_NONNUMERIC)
        table = [row for row in reader]

    print("Read file " + str(results_file) + ".")
    return table


def extract_grids(table: List[Dict], long_grid: TextGrid, directory: Path):
    """
    Extract and write individual TextGrids.
    
    Uses the timing info in table to slice long_grid and offset the new
    TextGrids correctly. Saves resulting TextGrids in directory.

    NOTE! Any existing TextGrids in outdirectory will be overwritten
    without confirmation
    """
    # TODO: Get the Tier names from config or the textgrid itself.
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

        textgrid = TextGrid(xmin = entry["sliceBegin"])
        textgrid.interval_tier_from_array("utterance", utterance)
        textgrid.interval_tier_from_array("word", word)
        textgrid.interval_tier_from_array("segment", segment)
        textgrid.interval_tier_from_array("Phonetic detail", detail)

        textgrid.offset_time(-entry["sliceBegin"])

        filename = (directory/entry['id']).with_suffix('.TextGrid')
        # TODO: Check for existing TextGrids and add a mechanism for resolving
        # overwrites via config and asking the user (and updating config
        # accordingly at runtime).
        textgrid.write(filename)
        i += 1

    return i


def extract_textgrids(
        outdirectory: Path, 
        results: Path,
    ):
    """
    Break a long TextGrid into recording specific ones.

    Reads the TextGrids specified by config (and produced by concatenate) and
    the results .csv file from the results argument. Writes individual TextGrids
    in outdirectory. 
    
    NOTE! Any existing TextGrids in outdirectory will be overwritten
    without confirmation
    """

    results_csv = results.with_suffix('.csv')
    grid_file = results.with_suffix('.TextGrid')

    table = read_results_csv(results_csv)

    long_grid = TextGrid(grid_file)
    print(f"Read {grid_file}.")

    i = extract_grids(table, long_grid, outdirectory)
    print(f'Wrote {i} textgrids.')

