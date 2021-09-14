
# import os
import glob
import json
import sys
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

def meta_and_tg(directory):
    """UTI metadata and Praat TextGrid parser

    Needs a description. Might be converted to a class in a bit.
    """
    grids = []
    pp = pprint.PrettyPrinter(indent=4)

    prompt_pattern = 'meta/*.txt' 
    uti_pattern = 'metaUS/*US.txt'
    grid_pattern = 'textgrid/*.TextGrid'

# This would be needed for the old directory structure where the 
# metafiles live jumbled together in the same directory.
#    prompt_pattern = '*.txt' 
#    uti_pattern = '*US.txt'
#    grid_pattern = '*.TextGrid'

    # Find UTI meta data files
    prompt_files = glob.glob(os.path.join(directory, prompt_pattern))
    uti_files = glob.glob(os.path.join(directory, uti_pattern))

# This would be needed for the old directory structure where the 
# metafiles live jumbled together in the same directory.
#    for filename in uti_files:
#        prompt_files.remove(filename)

    # Split first to get rid of the suffix, then to get rid of the path.
    prefixes = [filename.split('.')[-2].split('/').pop() 
                for filename in prompt_files]

    # double brackets to make fromkeys understand that 'name' is the key
    # not 'n' and 'a' and...
    name = [['name']]*len(prefixes) 

    # initialise grids with the prefixes of the sample files 
    grids = map(dict.fromkeys, name, prefixes)
    prefixdict = dict(zip(prefixes, grids))

    # Split first to get rid of the suffix, then to get rid of the path.
    utiprefixes = [filename.split('US.')[-2].split('/')[-1] 
                   for filename in uti_files]

    for (i, filename) in enumerate(uti_files):
        prefixdict[utiprefixes[i]]['utifile'] = utiprefixes[i] + '.ult'
        prefixdict[utiprefixes[i]]['wavfile'] = utiprefixes[i] + '.wav'
        prefixdict[utiprefixes[i]]['metafile'] = filename 

    # Read metadata file contents into the grid list.
    for (i, grid) in enumerate(grids):
        grid['UTIMeta'] = dict()
        if 'metafile' not in grid:
            grid['utifile'] = ''
            grid['metafile'] = ''
            grid['wavfile'] = ''
            grid['prompt'] = ''
            continue

        with open(grid['metafile'], 'r') as uti_file:
            for line in uti_file:
                line = line.strip().split('=')
                grids[i]['UTIMeta'][line[0]] = num(line[1])
        with open(prompt_files[i], 'r') as prompt_file:
            grid['prompt'] = prompt_file.readline().strip()

    for (i, grid) in enumerate(grids):
        grids[i]['TextGrid'] = dict()
        #
        # Ugly hack.
        # Edit this bit to correspond to your tier names.
        # Orignal has two tiers 'segment' and 'syllable'.
        grids[i]['TextGrid']['segment'] = []
        grids[i]['TextGrid']['syllable'] = []

    grids = tg(grids, prefixes, directory)

    #pp.pprint(prefixdict)
    return (grids, prefixes)


def tg(grids, prefixes, directory):
    grid_pattern = 'textgrid/*.TextGrid'

    # Find textgrid files and map their contents to textgrid objects
    gridfiles = glob.glob(os.path.join(directory, grid_pattern))
    gridnames = [filename.split('.')[-2].split('/').pop() 
                 for filename in gridfiles]
    textgrids = map(TextGridFromFile, gridfiles, gridnames)
    grid_index = [prefixes.index(gridname) for gridname in gridnames]

    # Parse textgrid intervals and points to the dictionaries
    # representing the samples.
    for (i, grid) in enumerate(textgrids):
        # Check that the different files line up and samples don't get
        # confused with other samples.
        if (grids[grid_index[i]]['name'] != grid.name):
            raise Error(
                'TextGrid filename does not match with corresponding ' 
                + 'metadata filename: ' 
                + grids[grid_index[i]]['name']
                + ' is not ' + grid.name + '.')

        for (tier) in grid.tiers:
            if hasattr(tier, 'intervals'):
                for interval in tier.intervals:
                    if len(interval.mark) == 0:
                        continue
                    grids[grid_index[i]]['TextGrid'][tier.name].append([
                        interval.minTime, interval.maxTime, interval.mark])
            else:
                for point in tier.points:
                    if len(point.mark) == 0:
                        continue
                    grids[grid_index[i]]['TextGrid'][point.mark] = point.time

    print("Processed " + str(len(textgrids)) + " TextGrids.")
    return grids



def write_json(grids, fileprefix):
    # Finally dump all the metadata into a json-formated file to
    # be read by matlab.
    # grids = {"data": grids}
    with open(fileprefix + '_segments.TGjson', 'w') as tgjson:
        json.dump(grids, tgjson, sort_keys=True, indent=2, 
                  separators=(',', ': '))
    print("Wrote file " + fileprefix + '_segments.TGjson')

def main(args):
    first_directory = args.pop()
    fileprefix = args.pop()
    (grids, prefixes) = meta_and_tg(first_directory)
    if len(args) > 0:
        for dirname in args:
            grids = tg(grids, prefixes, dirname)
    write_json(grids, fileprefix)

if (len(sys.argv) < 3):
    print("\nmeta_and_tg2json.py")
    print("\tusage: meta_and_tg2json.py fileprefix directory [more directories]")
    print("\n\tConverts UTI meta data and Praat text ")
    print("\tgrid contents into a matlab readable json file.")
    print("\n\tThe result of the example call would be written into ")
    print("\ta file named fileprefix_segments.TGjson.\n")
    sys.exit(0)

if (__name__ == '__main__'):
    main(sys.argv[1:])


        
    # # Find textgrid files and map their contents to textgrid objects
    # gridfiles = glob.glob(os.path.join(directory, grid_pattern))
    # gridnames = [filename.split('.')[-2].split('/').pop() 
    #              for filename in gridfiles]
    # textgrids = map(TextGridFromFile, gridfiles, gridnames)
    # grid_index = [prefixes.index(gridname) for gridname in gridnames]

    # # Parse textgrid intervals and points to the dictionaries
    # # representing the samples.
    # for (i, grid) in enumerate(textgrids):
    #     # Check that the different files line up and samples don't get
    #     # confused with other samples.
    #     if (grids[grid_index[i]]['name'] != grid.name):
    #         raise Error(
    #             'TextGrid filename does not match with corresponding ' 
    #             + 'metadata filename: ' 
    #             + grids[grid_index[i]]['name']
    #             + ' is not ' + grid.name + '.')

    #     for (tier) in grid.tiers:
    #         if hasattr(tier, 'intervals'):
    #             for interval in tier.intervals:
    #                 grids[grid_index[i]]['TextGrid'][interval.mark] = [
    #                     interval.minTime, interval.maxTime]
    #         else:
    #             for point in tier.points:
    #                 grids[grid_index[i]]['TextGrid'][point.mark] = point.time
