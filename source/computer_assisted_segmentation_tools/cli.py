#!/usr/bin/env python3
#
# Copyright (c) 2022-2024 Pertti Palo.
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

# import time

from .command_line import CastArgumentParser
from .commands import CommandStrings, process_command
from .configuration_parser import read_config_file
from .exclusion import load_exclusion_list


def run_cli():
    """
    Main to run CAST

    Parameters
    ----------
    args : list
        Command line arguments.
    """
    cli = CastArgumentParser("CAST")

    command_string = cli.args.command
    if command_string in CommandStrings.values():
        command = CommandStrings(command_string)
        config_filename = cli.args.configuration_filename
        config_dict = read_config_file(config_filename)
        if config_dict["exclusion_list"]:
            exclusion_filename = config_dict["exclusion_list"]
        else:
            exclusion_filename = cli.args.exclusion_filename
        exclusion_list = load_exclusion_list(exclusion_filename)
        path = config_dict['data_directory']

        process_command(command=command,
                        path=path,
                        config_dict=config_dict,
                        exclusion_list=exclusion_list)
    else:
        print("Did not find a command in the arguments: " +
              cli.args.command + ".")
        print(f"Accepted commands are: {', '.join(CommandStrings.values())}")


# if __name__ == '__main__':
#     start_time = time.perf_counter()
#     main()
#     elapsed_time = time.perf_counter() - start_time
#     print(f'Elapsed time was {elapsed_time}.')
