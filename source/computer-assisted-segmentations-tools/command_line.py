
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


class CastArgumentParser():
    """
    This class is the root class for CAST command line interfaces.

    This class is not fully functional by itself: It does not read files
    nor run any processing on files.
    """

    def __init__(self, description):
        """
        Setup a command line interface with the given description.

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
