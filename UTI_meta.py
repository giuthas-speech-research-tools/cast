
# import os
import glob
import csv
import json
import sys
import os.path
import string
import pprint

pp = pprint.PrettyPrinter(indent=4)


# Helper for parsing numbers that are only going to be written out
# again and thus we want to keep them in the same type as they
# originally were.
def num(s):
    try:
        return int(s)
    except ValueError:
        return float(s)

class Error(Exception):
    """Base class for exceptions in this module.

    Attributes:
        msg  -- explanation of the error
    """    
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


def init_grids(directory):
    


def add_trial(grid, trial):
    grid['trial'] = trial
    return grid


def parse_meta(grid):
    table = [{'id':'n/a', 
              'speaker':speaker_id, 
              'sliceBegin':'n/a',
              'beep':'n/a',
              'begin':'n/a', 
              'end':'n/a', 
              'word':'n/a'} 
             for i in range(len(wav_files))]

    # Read metadata file contents into the grid list.
    grid['UTIMeta'] = dict()
    if os.path.isfile('metaUS/'+grid['name']+'US.txt'):
        grid['metafile'] = 'metaUS/'+grid['name']+'US.txt'
    if os.path.isfile('meta/'+grid['name']+'.txt'):
        grid['promptfile'] = 'meta/'+grid['name']+'.txt'
    if os.path.isfile('sound/'+grid['name']+'.wav'):
        grid['wavfile'] = 'sound/'+grid['name']+'.wav'
    if os.path.isfile('uti/'+grid['name']+'.ult'):
        grid['utifile'] = 'uti/'+grid['name']+'.ult'

    with open(grid['metafile'], 'r') as uti_file:
        for line in uti_file:
            line = line.strip().split('=')
            grid['UTIMeta'][line[0]] = num(line[1])
    with open(grid['promptfile'], 'r') as prompt_file:
        grid['prompt'] = prompt_file.readline().strip()
        (date, time) = prompt_file.readline().strip().split(" ")
        grid['date'] = date
        grid['time'] = time
        grid['participant'] = prompt_file.readline().strip() #poista pilkku
              
    return grid


def write_csv(grids, filename):
    # Finally dump all the metadata into a csv-formated file to
    # be read by R.
    with open(filename + '_segments.csv', 'w') as csvfile:
        fieldnames = ['name', 'trial', 'word', 'type', 
                      'C1', 'C2', 'C3', 'V', 'Cf', 
                      'C1_dur', 'C2_dur', 'C3_dur', 'V_dur', 'Cf_dur', 
                      'beep', 'ac_RT', 'ac_onset', 'ac_od', 
                      'mo', 'cr', 'vr']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        map(writer.writerow, grids)

    print("Wrote file " + filename + '_segments.csv')


def write_json(grids, fileprefix):
    # Finally dump all the metadata into a csv-formated file to
    # be read by R.
    with open(fileprefix + '_segments.TGjson', 'w') as tgjson:
        json.dump(grids, tgjson, sort_keys=True, indent=2, 
                  separators=(',', ': '))
    print("Wrote file " + fileprefix + '_segments.TGjson')


def main(args):
    dirname = args[1:]
    grids = init_grids(directory)
    #directory = dirnames.pop()
#    grids = map(scale_variables, grids)
    grids = map(add_trial, grids, range(1, len(grids)+1))
    write_csv(grids, args[0])
    grids = map(parse_meta, grids)
    write_json(grids, args[0])


if (len(sys.argv) < 2):
    print("\nUTI_meta.py")
    print("\n***Unfinished! Don't trust the instructions below.")
    print("\tusage: python UTI_meta.py directory")
    print("\n\tReads contents of an experiment (day) directory and")
    print("\tproduces an R readable csv file containing meta data. ")
    print("\n\tThe result of the example call would be written into ")
    print("\ta file named fileprefix_segments.csv.\n")
    print("\tRegularly used by other scripts as meta importer.\n")
    sys.exit(0)

if (__name__ == '__main__'):
    main(sys.argv[1:])
