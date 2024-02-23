#!/usr/bin/env python3
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

from cast.commands import CommandStrings, process_command
from cast.configuration import read_config_file


def main(args: list):
    """
    Main to run CAST

    Parameters
    ----------
    args : list
        Command line arguments.
    """
    command = None
    config_filename = None
    if args and args[0] in CommandStrings.values():
        command = CommandStrings(args[0])
        config_filename = args.pop()
        config_dict = read_config_file(config_filename)
        path = config_dict['data directory']

        process_command(command=command,
                        path=path,
                        config_dict=config_dict)
    else:
        print("Did not find a command in the arguments: " +
              str(args) + ".")
        print(f"Accepted commands are: {', '.join(CommandStrings.values())}")


if (len(sys.argv) not in [2, 3] or '-h' in sys.argv):
    print("\ncast.py")
    print("\tusage: cast.py add [config-yaml-file]")
    print("\tusage: cast.py concatenate [config-yaml-file]")
    print("\tusage: cast.py extract [config-yaml-file]")
    print("\tusage: cast.py remove-double-word-boundaries [config-yaml-file]")
    print("\n\tConcatenates wav files and creates a corresponding TextGrid.")
    print("\tWrites a huge wav-file, a corresponding textgrid, and")
    print("\ta metafile to assist in extracting shorter textgrid after annotation.")
    print("\n\tAll options are provided by the config file which defaults to cast_config.yml.")
    sys.exit(0)


if __name__ == '__main__':
    start_time = time.perf_counter()
    main(sys.argv[1:])
    elapsed_time = time.perf_counter() - start_time
    print(f'Elapsed time was {elapsed_time}.')
