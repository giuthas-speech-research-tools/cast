
# import os
import glob
import csv
import json
import sys
import string
import pprint
from textgrid import *

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

# Version of tgFromFile which is safe to run on potentially 
# non-existent files.
def tgFromFileWrapper(filename, gridname):
    if os.path.isfile(filename):
        try:
            return TextGridFromFile(filename, gridname)
        except ValueError as e:
            print 'ValueError', e, 'is a duplicate.'
            print('In file ' + filename + '.')
            return None
    else:
        return None


def promptFromPath(filepath, gridname):
    if not os.path.isfile(filepath):
        return None
    
    grid = {'name': gridname}
    with open(filepath, 'r') as prompt_file:
        grid['prompt'] = prompt_file.readline().strip()

    return grid


def metaFromPath(filepath, gridname):
    grid = {'name': gridname} 
    grid['UTIMeta'] = dict()
    grid['utifile'] = ''
    grid['metafile'] = ''
    grid['wavfile'] = ''

    if os.path.isfile(filepath):
        grid['metafile'] = filepath
        grid['utifile'] = gridname + '.ult'
        grid['wavfile'] = gridname + '.wav'

        with open(grid['metafile'], 'r') as uti_file:
            for line in uti_file:
                line = line.strip().split('=')
                grid['UTIMeta'][line[0]] = num(line[1])

    return grid


def meta_and_tg(directory):
    pattern = 'meta/*.txt' 
    # pattern = 'textgrid/*.TextGrid'

    # Find and read ultrasound metadata and prompts
    prompt_files = glob.glob(os.path.join(directory, pattern))
    filenames = [filepath.split('.')[-2].split('/').pop() 
                for filepath in prompt_files]
    prompts = map(promptFromPath, prompt_files, filenames)

    metafiles = [string.replace(filepath, '.txt', 'US.txt')
                 for filepath in prompt_files]
    metafiles = [string.replace(filepath, 'meta', 'metaUS')
                 for filepath in metafiles]
    meta_data = map(metaFromPath, metafiles, filenames)

    # Find textgrid files and map their contents to textgrid objects
    gridfiles = [string.replace(filepath, 'txt', 'TextGrid')
                 for filepath in prompt_files]
    gridfiles = [string.replace(filepath, 'meta', 'textgrid')
                 for filepath in gridfiles]
    acoustic_grids = map(tgFromFileWrapper, gridfiles, filenames)

    gridfiles = [string.replace(filepath, 'textgrid', 'artic_annotations')
                 for filepath in gridfiles]
    articulatory_grids = map(tgFromFileWrapper, gridfiles, filenames)

    # Combine the metadata and textgrids.
    grids = map(ac_and_art2dict, 
                prompts, meta_data, 
                acoustic_grids, articulatory_grids)
    return grids


def ac_and_art2dict(prompt, meta, acoustic, articulatory):
    grid = prompt.copy()

#    print prompt['name']

    grid['word'] = 'NA'
    grid['type'] = 'NA'
    grid['C1'] = 'NA'
    grid['C2'] = 'NA'
    grid['C3'] = 'NA'
    grid['V'] = 'NA'
    grid['Cf'] = 'NA'
    grid['beep'] = 'NA'
    grid['ac_RT'] = 'NA'
    grid['ac_onset'] = 'NA'
    grid['ac_od'] = 'NA'
    grid['mo'] = 'NA'
    grid['cr'] = 'NA'
    grid['vr'] = 'NA'

    if meta is not None:
        grid.update(meta)

    if acoustic is not None:

        if (acoustic.tiers[0].intervals[0].mark == 'n/a' or 
            acoustic.tiers[0].intervals[0].mark == 'na'):
            return grid

        grid['word'] = acoustic.tiers[0].intervals[1].mark

        if acoustic.tiers[1].intervals[2].mark in 'aiO':
            grid['type'] = 'VC'
            grid['V'] = acoustic.tiers[1].intervals[2].mark
            grid['ac_od'] = 0
            if len(acoustic.tiers[1].intervals) > 3:
                grid['Cf'] = acoustic.tiers[1].intervals[3].mark
        elif acoustic.tiers[1].intervals[3].mark in 'aiO':
            grid['type'] = 'CVC'
            grid['C1'] = acoustic.tiers[1].intervals[2].mark
            grid['V'] = acoustic.tiers[1].intervals[3].mark
            grid['ac_od'] = acoustic.tiers[1].intervals[2].duration()
            if len(acoustic.tiers[1].intervals) > 4:
                grid['Cf'] = acoustic.tiers[1].intervals[4].mark
        elif acoustic.tiers[1].intervals[4].mark in 'aiO':
            grid['type'] = 'CCVC'
            grid['C1'] = acoustic.tiers[1].intervals[2].mark
            grid['C2'] = acoustic.tiers[1].intervals[3].mark
            grid['V'] = acoustic.tiers[1].intervals[4].mark
            grid['ac_od'] = acoustic.tiers[1].intervals[2].duration() 
            grid['ac_od'] += acoustic.tiers[1].intervals[3].duration()

            if len(acoustic.tiers[1].intervals) > 5:
                grid['Cf'] = acoustic.tiers[1].intervals[5].mark
        else:
            grid['type'] = 'CCCVC'
            grid['C1'] = acoustic.tiers[1].intervals[2].mark
            grid['C2'] = acoustic.tiers[1].intervals[3].mark
            grid['C3'] = acoustic.tiers[1].intervals[4].mark
            grid['V'] = acoustic.tiers[1].intervals[5].mark
            grid['ac_od'] = acoustic.tiers[1].intervals[2].duration()
            grid['ac_od'] += acoustic.tiers[1].intervals[3].duration()
            grid['ac_od'] += acoustic.tiers[1].intervals[4].duration()

            if len(acoustic.tiers[1].intervals) > 6:
                grid['Cf'] = acoustic.tiers[1].intervals[6].mark

        grid['beep'] = acoustic.tiers[1].intervals[0].maxTime
        grid['ac_RT'] = acoustic.tiers[1].intervals[1].duration()
        grid['ac_onset'] = acoustic.tiers[1].intervals[1].maxTime

    if articulatory is not None:
        for point in articulatory.tiers[0].points:
            if len(point.mark) == 0:
                continue
            grid[point.mark] = point.time

    return grid


def write_csv(grids, directory):
    # Finally dump all the metadata into a csv-formated file to
    # be read by R.
    with open(directory + '_grids_and_meta.csv', 'w') as csvfile:
        fieldnames = ['name', 'word', 'type', 'C1', 'C2', 'C3', 'V', 
                      'Cf', 'beep', 'ac_RT', 
                      'ac_onset', 'ac_od', 'mo', 'cr', 'vr']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        map(writer.writerow, grids)

    print("Wrote file " + directory + '_grids_and_meta.csv')

def write_json(grids, directory):
    # Finally dump all the metadata into a json-formated file to
    # be read by matlab.
    with open(directory + '_grids_and_meta.json', 'w') as tgjson:
        json.dump(grids, tgjson, sort_keys=True, indent=2, 
                  separators=(',', ': '))
    print("Wrote file " + directory + '_grids_and_meta.json')

def main(dirnames):
    directory = dirnames.pop()
    (grids) = meta_and_tg(directory)
    write_json(grids, directory)

if (len(sys.argv) < 2):
    print("\nex2_2_json_or_csv.py")
    print("\tusage: ex2_2_json_or_csv.py directory")
    print("\n\tConverts Praat textgrid and ultrasound metadata contents into")
    print("\tan R readable csv and a Matlab readable json file.")
    print("\n\tThe result of the example call would be written into ")
    print("\ta file named directory_grids_and_meta.[TGjson/csv].\n")
    print("\nAt the moment csv output is disabled because it cannot handle nested dictionaries.\n")
    sys.exit(0)

if (__name__ == '__main__'):
    main(sys.argv[1:])
