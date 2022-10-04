
# import os
import csv
import glob
import json
import pprint
import sys
import string
import time
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

def tgFromFileWrapper(filename, gridname):
    if os.path.isfile(filename):
#        print filename
        return TextGridFromFile(filename, gridname)
    else:
        return None

def tg(directory):
    pattern = 'sound/*.TextGrid'

    # Find textgrid files and map their contents to textgrid objects
    gridfiles = glob.glob(os.path.join(directory, pattern))
    gridnames = [filename.split('.')[-2].split('/').pop() 
                 for filename in gridfiles]
    acoustic_grids = map(tgFromFileWrapper, gridfiles, gridnames)
    #TextGridFromFile

    gridfiles = [string.replace(filepath, 'sound', 'artic_annotations')
                 for filepath in gridfiles]
    articulatory_grids = map(tgFromFileWrapper, gridfiles, gridnames)

    grids = map(ac_and_art2dict, acoustic_grids, articulatory_grids)
    
    return grids


def ac_and_art2dict(acoustic, articulatory):
# Use this construction to switch on number of intervals in segment tier 
# and then select the correct combination of lengths to record: 
# C1, C2, asp, V, C_end + OD and OD_asp
# options = {0 : zero,
#                 1 : sqr,
#                 4 : sqr,
#                 9 : sqr,
#                 2 : even,
#                 3 : prime,
#                 5 : prime,
#                 7 : prime,
# }
 
# def zero():
#     print "You typed zero.\n"
 
# def sqr():
#     print "n is a perfect square\n"
 
# def even():
#     print "n is an even number\n"
 
# def prime():
#     print "n is a prime number\n"

    grid = {'name': acoustic.name}

    grid['word'] = 'NA'
    grid['trial'] = 'NA'
    grid['type'] = 'NA'
    grid['C1'] = '#' # hash stands for 'no C1'
    grid['C2'] = 'NA'
    grid['C3'] = 'NA'
    grid['V'] = 'NA'
    grid['Cf'] = 'NA'
    grid['C1_dur'] = 0.0
    grid['C2_dur'] = 0.0
    grid['C3_dur'] = 0.0
    grid['V_dur'] = 0.0
    grid['Cf_dur'] = 0.0
    grid['beep'] = 'NA'
    grid['ac_RT'] = 'NA'
    grid['ac_onset'] = 'NA'
    grid['ac_od'] = 'NA'
    grid['mo'] = 'NA'
    grid['cr'] = 'NA'
    grid['vr'] = 'NA'

    if(not acoustic):
        print "Warning an acoustic TextGrid was None."
        return grid

    if len(acoustic.tiers[1].intervals) < 4:
        print "Warning a Textgrid was too short:", acoustic, acoustic.tiers[1].intervals
        return grid

    if (acoustic.tiers[0].intervals[0].mark == 'n/a' or 
        acoustic.tiers[0].intervals[0].mark == 'na'):
        return grid

    grid['word'] = acoustic.tiers[0].intervals[1].mark
    if grid['word'] == 'pete':
        grid['word'] = 'Pete'
    

    if len(grid['word']) == 1:
        # Finnish data
        grid['type'] = 'V'
        grid['V'] = grid['word']
        grid['V_dur'] = acoustic.tiers[1].intervals[2].duration()
        grid['ac_od'] = 0.0
    elif len(grid['word']) == 2 and grid['word'][1] in 'aiu':
        # Finnish data
        grid['type'] = 'CV'
        grid['C1'] = grid['word'][0]
        grid['V'] = grid['word'][1]
        grid['C1_dur'] = acoustic.tiers[1].intervals[2].duration()
        grid['V_dur'] = acoustic.tiers[1].intervals[3].duration()
        grid['ac_od'] = grid['C1_dur']
    elif (acoustic.tiers[1].intervals[2].mark == 'h' and 
        acoustic.tiers[1].intervals[3].mark == 'w'):
        # pre-aspirated 'what'
        grid['type'] = 'CVC'
        grid['C1'] = acoustic.tiers[1].intervals[3].mark
        grid['V'] = acoustic.tiers[1].intervals[4].mark
        grid['C1_dur'] = (acoustic.tiers[1].intervals[2].duration() +
                          acoustic.tiers[1].intervals[3].duration())
        grid['ac_od'] = grid['C1_dur']
        # something like this with the others as well?
        # should probably check that mark[5] is something sensible?
        if len(acoustic.tiers[1].intervals) > 4:
            grid['V_dur'] = acoustic.tiers[1].intervals[4].duration()
        if len(acoustic.tiers[1].intervals) > 5:
            grid['Cf'] = acoustic.tiers[1].intervals[5].mark
        if (len(acoustic.tiers[1].intervals) > 6 and 
            acoustic.tiers[1].intervals[6].mark == '^h'):
            grid['Cf_dur'] = acoustic.tiers[1].intervals[5].duration()
    elif acoustic.tiers[1].intervals[2].mark in 'aiO':
        grid['type'] = 'VC'
        grid['V'] = acoustic.tiers[1].intervals[2].mark
        grid['V_dur'] = acoustic.tiers[1].intervals[2].duration()
        grid['ac_od'] = 0.0
        if len(acoustic.tiers[1].intervals) > 3:
            grid['Cf'] = acoustic.tiers[1].intervals[3].mark
        if (len(acoustic.tiers[1].intervals) > 4 and 
            acoustic.tiers[1].intervals[4].mark == '^h'):
            grid['Cf_dur'] = acoustic.tiers[1].intervals[3].duration()
    elif acoustic.tiers[1].intervals[3].mark in 'aiO':
        # basic CVC
        grid['type'] = 'CVC'
        grid['C1'] = acoustic.tiers[1].intervals[2].mark
        grid['V'] = acoustic.tiers[1].intervals[3].mark
        grid['C1_dur'] = acoustic.tiers[1].intervals[2].duration()
        grid['V_dur'] = acoustic.tiers[1].intervals[3].duration()
        grid['ac_od'] = grid['C1_dur']
        if len(acoustic.tiers[1].intervals) > 4:
            grid['Cf'] = acoustic.tiers[1].intervals[4].mark
        if (len(acoustic.tiers[1].intervals) > 5 and 
            acoustic.tiers[1].intervals[5].mark == '^h'):
            grid['Cf_dur'] = acoustic.tiers[1].intervals[4].duration()
    elif acoustic.tiers[1].intervals[3].mark == '^h':
        if acoustic.tiers[1].intervals[4].mark in 'aiO':
            # PVC
            grid['type'] = 'CVC'
            grid['C1'] = acoustic.tiers[1].intervals[2].mark
            grid['V'] = acoustic.tiers[1].intervals[4].mark
            grid['C1_dur'] = (acoustic.tiers[1].intervals[2].duration() +
                              acoustic.tiers[1].intervals[3].duration())
            grid['V_dur'] = acoustic.tiers[1].intervals[4].duration()
            grid['ac_od'] = grid['C1_dur']
            if len(acoustic.tiers[1].intervals) > 5:
                grid['Cf'] = acoustic.tiers[1].intervals[5].mark
                if (len(acoustic.tiers[1].intervals) > 6 and 
                    acoustic.tiers[1].intervals[6].mark == '^h'):
                    grid['Cf_dur'] = acoustic.tiers[1].intervals[5].duration()
        elif acoustic.tiers[1].intervals[5].mark in 'aiO':
            # pre-voiced PCVC
            grid['type'] = 'CCVC'
            grid['C1'] = acoustic.tiers[1].intervals[2].mark
            grid['C2'] = acoustic.tiers[1].intervals[4].mark
            grid['V'] = acoustic.tiers[1].intervals[5].mark
            grid['C1_dur'] = (acoustic.tiers[1].intervals[2].duration() +
                              acoustic.tiers[1].intervals[3].duration())
            grid['C2_dur'] = acoustic.tiers[1].intervals[4].duration()
            grid['V_dur'] = acoustic.tiers[1].intervals[5].duration()
            grid['ac_od'] = grid['C1_dur']
            if len(acoustic.tiers[1].intervals) > 6:
                grid['Cf'] = acoustic.tiers[1].intervals[6].mark
                if (len(acoustic.tiers[1].intervals) > 6 and 
                    acoustic.tiers[1].intervals[7].mark == '^h'):
                    grid['Cf_dur'] = acoustic.tiers[1].intervals[6].duration()
    elif acoustic.tiers[1].intervals[4].mark in 'aiO':
        # basic CCVC
        grid['type'] = 'CCVC'
        grid['C1'] = acoustic.tiers[1].intervals[2].mark
        grid['C2'] = acoustic.tiers[1].intervals[3].mark
        grid['V'] = acoustic.tiers[1].intervals[4].mark
        grid['C1_dur'] = acoustic.tiers[1].intervals[2].duration()
        grid['C2_dur'] = acoustic.tiers[1].intervals[3].duration()
        grid['V_dur'] = acoustic.tiers[1].intervals[4].duration()
        grid['ac_od'] = grid['C1_dur'] + grid['C2_dur']
        if len(acoustic.tiers[1].intervals) > 5:
            grid['Cf'] = acoustic.tiers[1].intervals[5].mark
        if (len(acoustic.tiers[1].intervals) > 6 and 
            acoustic.tiers[1].intervals[6].mark == '^h'):
            grid['Cf_dur'] = acoustic.tiers[1].intervals[5].duration()
    elif (acoustic.tiers[1].intervals[4].mark == '^h' and
          acoustic.tiers[1].intervals[5].mark in 'aiO'):
        # CPVC, P for Plosive
        grid['type'] = 'CCVC'
        grid['C1'] = acoustic.tiers[1].intervals[2].mark
        grid['C2'] = acoustic.tiers[1].intervals[3].mark
        grid['V'] = acoustic.tiers[1].intervals[5].mark
        grid['C1_dur'] = acoustic.tiers[1].intervals[2].duration()
        grid['C2_dur'] = (acoustic.tiers[1].intervals[3].duration() +
                          acoustic.tiers[1].intervals[4].duration())
        grid['V_dur'] = acoustic.tiers[1].intervals[5].duration()
        grid['ac_od'] = grid['C1_dur'] + grid['C2_dur']
        if len(acoustic.tiers[1].intervals) > 6:
            grid['Cf'] = acoustic.tiers[1].intervals[6].mark
        if (len(acoustic.tiers[1].intervals) > 7 and 
            acoustic.tiers[1].intervals[7].mark == '^h'):
            grid['Cf_dur'] = acoustic.tiers[1].intervals[6].duration()
    elif acoustic.tiers[1].intervals[5].mark in 'aiO':
        # aspiration not segmented
        grid['type'] = 'CCCVC'
        grid['C1'] = acoustic.tiers[1].intervals[2].mark
        grid['C2'] = acoustic.tiers[1].intervals[3].mark
        grid['C3'] = acoustic.tiers[1].intervals[4].mark
        grid['V'] = acoustic.tiers[1].intervals[5].mark
        grid['C1_dur'] = acoustic.tiers[1].intervals[2].duration()
        grid['C2_dur'] = acoustic.tiers[1].intervals[3].duration()
        grid['C3_dur'] = acoustic.tiers[1].intervals[4].duration()
        grid['V_dur'] = acoustic.tiers[1].intervals[5].duration()
        grid['ac_od'] = grid['C1_dur'] + grid['C2_dur'] + grid['C3_dur']
        if len(acoustic.tiers[1].intervals) > 6:
            grid['Cf'] = acoustic.tiers[1].intervals[6].mark
        if (len(acoustic.tiers[1].intervals) > 7 and 
            acoustic.tiers[1].intervals[7].mark == '^h'):
            grid['Cf_dur'] = acoustic.tiers[1].intervals[6].duration()
    else:
        # aspiration segmented
        grid['type'] = 'CCCVC'
        grid['C1'] = acoustic.tiers[1].intervals[2].mark
        grid['C2'] = acoustic.tiers[1].intervals[3].mark
        grid['C3'] = acoustic.tiers[1].intervals[5].mark
        grid['V'] = acoustic.tiers[1].intervals[6].mark
        grid['C1_dur'] = acoustic.tiers[1].intervals[2].duration()
        grid['C2_dur'] = (acoustic.tiers[1].intervals[3].duration() +
                          acoustic.tiers[1].intervals[4].duration())
        grid['C3_dur'] = acoustic.tiers[1].intervals[5].duration()
        grid['V_dur'] = acoustic.tiers[1].intervals[6].duration()
        grid['ac_od'] = grid['C1_dur'] + grid['C2_dur'] + grid['C3_dur']
        if len(acoustic.tiers[1].intervals) > 7:
            grid['Cf'] = acoustic.tiers[1].intervals[7].mark
        if (len(acoustic.tiers[1].intervals) > 8 and 
            acoustic.tiers[1].intervals[8].mark == '^h'):
            grid['Cf_dur'] = acoustic.tiers[1].intervals[7].duration()

    grid['beep'] = acoustic.tiers[1].intervals[0].maxTime
    grid['ac_RT'] = acoustic.tiers[1].intervals[1].duration()
    grid['ac_onset'] = acoustic.tiers[1].intervals[1].maxTime

    if articulatory is not None:
        if len(articulatory.tiers[0].points) < 1:
            print "Warning a Textgrid was too short", 
            articulatory.tiers[0].points
        else:
            for point in articulatory.tiers[0].points:
                if len(point.mark) == 0 or point.mark == "new":
                    grid['mo'] = point.time
                else:
                    grid[point.mark] = point.time
    else:
        # if we've come this far, the acoustic grid is not None.
        print("Warning an articulatory TextGrid was None. Acoustic was:" + 
              str(acoustic))
        return grid

    return grid


def scale_variables(grid):
    for key in grid.keys():
        if isinstance(grid[key], float):
            grid[key] = 1000*grid[key]
    return grid


def reverse_scale_variables(grid):
    for key in grid.keys():
        if isinstance(grid[key], float):
            grid[key] = grid[key]/1000
    return grid


def add_trial(grid, trial):
    grid['trial'] = trial
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


def parse_meta(grid):
    # Read metadata file contents into the grid list.
    grid['UTIMeta'] = dict()
    grid['metafile'] = 'metaUS/'+grid['name']+'US.txt'
    grid['promptfile'] = 'meta/'+grid['name']+'.txt'
    grid['wavfile'] = 'sound/'+grid['name']+'.wav'
    grid['utifile'] = 'uti/'+grid['name']+'.ult'

    with open(grid['metafile'], 'r') as uti_file:
        for line in uti_file:
            line = line.strip().split('=')
            grid['UTIMeta'][line[0]] = num(line[1])
    with open(grid['promptfile'], 'r') as prompt_file:
        grid['prompt'] = prompt_file.readline().strip()
              
    return grid

def write_json(grids, fileprefix):
    # Finally dump all the metadata into a csv-formated file to
    # be read by R.
    with open(fileprefix + '_segments.TGjson', 'w') as tgjson:
        json.dump(grids, tgjson, sort_keys=True, indent=2, 
                  separators=(',', ': '))
    print("Wrote file " + fileprefix + '_segments.TGjson')


def main(args):
    dirnames = args[1:]
    directory = dirnames.pop()
    (grids) = tg(directory)
    grids = map(scale_variables, grids)
    grids = map(add_trial, grids, range(1, len(grids)+1))
    write_csv(grids, args[0])
    grids = map(reverse_scale_variables, grids)
    grids = map(parse_meta, grids)
    write_json(grids, args[0])


if (len(sys.argv) < 3):
    print("\ntextgrid2csv.py")
    print("\tusage: textgrid2csv.py fileprefix directory")
    print("\n\tConverts Praat textgrid contents into")
    print("\nan R readable csv file. ")
    print("\n\tThe result of the example call would be written into ")
    print("\ta file named fileprefix_segments.csv.\n")
    sys.exit(0)

if (__name__ == '__main__'):
    t = time.time()
    main(sys.argv[1:])
    print 'Elapsed time', (time.time() - t)
