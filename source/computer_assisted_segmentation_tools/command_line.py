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

"""
Command line argument parser.
"""

import argparse
import warnings

from .commands import CommandStrings


def widen_help_formatter(formatter, total_width=140, syntax_width=35):
    """Return a wider HelpFormatter for argparse, if possible."""
    try:
        # https://stackoverflow.com/a/5464440
        # beware: "Only the name of this class is considered a public API."
        kwargs = {'width': total_width, 'max_help_position': syntax_width}
        formatter(None, **kwargs)
        return lambda prog: formatter(prog, **kwargs)
    except TypeError:
        warnings.warn(
            "Widening argparse help formatter failed. "
            "Falling back on default settings.")
    return formatter


class CastArgumentParser:
    """
    This class is the root class for CAST command line interfaces.

    This class is not fully functional by itself: It does not read files
    nor run any processing on files.
    """

    def __init__(self, description):
        """
        Set up a command line interface with the given description.

        Sets up the parsers and runs it, and also sets up logging. Description
        is what this version will be called if called with -h or --help.
        """
        self.description = description
        self.parser = argparse.ArgumentParser(
            description=self.description,
            formatter_class=widen_help_formatter(
                argparse.HelpFormatter, total_width=80, syntax_width=35))

        self._add_positional_arguments()
        self._add_optional_arguments()
        self.args = self.parser.parse_args()

    def _add_optional_arguments(self):
        """Adds arguments."""

        helptext = (
            'Use the given configuration file. '
        )
        self.parser.add_argument("-c", "--configuration",
                                 dest="configuration_filename",
                                 help=helptext, metavar="file")

        helptext = (
            "Exclusion list of data files that should be ignored. "
            "Overrides the exclusion list in the config file."
        )
        self.parser.add_argument(
            "-e", "--exclusion_list", dest="exclusion_filename",
            help=helptext,
            metavar="file")

        helptext = (
            'Set verbosity of console output. Range is [0, 3], default is 1, '
            'larger values mean greater verbosity.'
        )
        self.parser.add_argument("-v", "--verbose",
                                 type=int, dest="verbose",
                                 default=1,
                                 help=helptext,
                                 metavar="verbosity")

    def _add_positional_arguments(self):
        """Setup basic command line parsing and the file loading argument."""
        helptext = (
            'Command to be run. ' +
            'Accepted commands are ' +
            ', '.join(CommandStrings.values()) + '.'
        )
        self.parser.add_argument("command", help=helptext)

        helptext = (
            'Path to the original data.'
        )
        self.parser.add_argument("path", help=helptext)
