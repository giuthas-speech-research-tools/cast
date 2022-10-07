
import csv
from contextlib import closing


def write_fav_input(table, filename):
    """
    Write the metadata into a csv-formated file to be read by FAVE.
    """
    # extrasaction='ignore' does not seem to be working so we do this the long way
    fieldnames = ['id', 'speaker', 'begin', 'end', 'word']
    results = [{key: entry[key] for key in fieldnames} for entry in table]

    with closing(open(filename, 'w')) as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, 
                                delimiter='\t', quoting=csv.QUOTE_NONE)

        list(map(writer.writerow, results))
    print("Wrote file " + filename + " for FAVE align.")


def write_results(table, filename, detect_beep):
    """ 
    Write the metadata into a csv-formated file to be read by Python or R.

    This file is meant for the extraction script but also possibly
    used by later analysis stages.
    """
    # extrasaction='ignore' does not seem to be working so we do this the long way
    if detect_beep:
        fieldnames = ['id', 'speaker', 'sliceBegin', 'beep', 'begin', 'sliceEnd', 'prompt']
    else: 
        fieldnames = ['id', 'speaker', 'sliceBegin', 'begin', 'sliceEnd', 'prompt']
    results = [{key: entry[key] for key in fieldnames} for entry in table]

    with closing(open(filename, 'w')) as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames,
                                quoting=csv.QUOTE_NONNUMERIC)

        writer.writeheader()
        list(map(writer.writerow, results))
    print(f"Wrote file {filename} for R/Python.")
