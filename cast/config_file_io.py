
from contextlib import closing
import csv
import os
import sys

def read_na_list(dirname):
    """
    Read the exclusion list from na_list.txt.
    
    If no exclusioin list file is present, return an empty array
    after warning the user.
    """
    na_file = os.path.join(dirname, 'na_list.txt')
    if os.path.isfile(na_file):
        na_list = [line.rstrip('\n') for line in open(na_file)]
    else:
        na_list = []
        print("Didn't find na_list.txt. Proceeding anyhow.")
    return na_list



def read_pronunciation_dict(filename):
    """
    Read the pronuciation dictionary and return it as a dict.

    The file is assumed to be in tab separated format and to 
    contain one word on each line followed by the X-SAMPA transcription
    of the expected pronunciation (phonological transcription).

    Returns a dict where each entry is a list of phonomes.
    """
    pronunciation_dict = {}
    if os.path.isfile(filename):
        with closing(open(filename, 'r')) as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            pronunciation_dict = {row[0]: list(filter(None, row[1:])) for row in reader}
        return pronunciation_dict
    else:
        print("Didn't find {pronunciation_dict}. Exiting.", pronunciation_dict)
        sys.exit()
