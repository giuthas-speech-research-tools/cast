#
# Copyright (c) 2022-2023 Pertti Palo.
#
# This file is part of Computer Assisted Segmentation Tools 
# (see https://github.com/giuthas-speech-research-tools/cast/).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# The example data packaged with this program is licensed under the
# Creative Commons Attribution-NonCommercial-ShareAlike 4.0
# International (CC BY-NC-SA 4.0) License. You should have received a
# copy of the Creative Commons Attribution-NonCommercial-ShareAlike 4.0
# International (CC BY-NC-SA 4.0) License along with the data. If not,
# see <https://creativecommons.org/licenses/by-nc-sa/4.0/> for details.
#
# When using the toolkit for scientific publications, please cite the
# articles listed in README.markdown. They can also be found in
# citations.bib in BibTeX format.
#

import sys
import time
from pathlib import Path

from cast import (add_tiers, concatenate_wavs, extract_textgrids, read_config_file,
                  read_pronunciation_dict,
                  remove_empty_intervals_from_textgrids)


def main(args):
    command = None
    config_filename = None
    if args and args[0] in ('add', 'concatenate', 'extract', 'remove-double-word-boundaries'):
        command = args[0]
        config_filename = args[1]
    elif args:
        print("Did not find a command in the arguments: " + args + " Concatenating.")
        command = 'concatenate'
        config_filename = args.pop()
    config_dict = read_config_file(config_filename)

    speaker_id = config_dict['speaker id']
    original_dirname = config_dict['data directory']
    outfilename = config_dict['outputfilename']

    detect_beep = config_dict['flags']['detect beep']
    test = config_dict['flags']['test']

    if command == 'add':
        if not config_dict['flags']['only words']:
            pronunciation_dict = read_pronunciation_dict(config_dict['pronunciation dictionary'])
            add_tiers(speaker_id, original_dirname, outfilename, config_dict, 
                pronunciation_dict=pronunciation_dict, test=test, detect_beep=detect_beep)
    elif command == 'concatenate':
        if not config_dict['flags']['only words']:
            pronunciation_dict = read_pronunciation_dict(config_dict['pronunciation dictionary'])
            concatenate_wavs(speaker_id, original_dirname, outfilename, config_dict, 
                pronunciation_dict=pronunciation_dict, test=test, detect_beep=detect_beep)
        else:
            concatenate_wavs(speaker_id, original_dirname, outfilename, config_dict, 
                test=test, detect_beep=detect_beep)
    elif command == 'remove-double-word-boundaries':
        if not config_dict['output_dirname']:
            print('Fatal: No output directory for new textgrids specified in ' + config_filename + '.')
        remove_empty_intervals_from_textgrids(Path(original_dirname), Path(config_dict['output_dirname']))
    else:
        extract_textgrids(Path(original_dirname), Path(outfilename))


if (len(sys.argv) not in [1,2,3] or '-h' in sys.argv):
    print("\ncast.py")
    print("\tusage: cast.py [config-yaml-file]")
    print("\tusage: cast.py add [config-yaml-file]")
    print("\tusage: cast.py concatenate [config-yaml-file]")
    print("\tusage: cast.py extract [config-yaml-file]")
    print("\tusage: cast.py remove-double-word-boundaries [config-yaml-file]")
    print("\n\tConcatenates wav files and creates a corresponding TextGrid.")
    print("\tWrites a huge wav-file, a corresponding textgrid, and")
    print("\ta metafile to assist in extracting shorter textgrid after annotation.")
    print("\n\tAll options are provided by the config file which defaults to cast_config.yml.")
    sys.exit(0) 


if (__name__ == '__main__'):
    start_time = time.perf_counter()
    main(sys.argv[1:])
    elapsed_time = time.perf_counter() - start_time
    print(f'Elapsed time was {elapsed_time}.')
