from enum import Enum
from pathlib import Path
from .clean_textgrids import remove_empty_intervals_from_textgrids
from .concatenate import concatenate_wavs

from .configuration import read_pronunciation_dict
from .extract import extract_textgrids
from .textgrid_functions import add_tiers


class CommandStrings(Enum):
    """
    Commands accepted by CAST as strings.
    """
    ADD = 'add'
    CONCATENATE = 'concatenate'
    EXTRACT = 'extract'
    REMOVE_DOUBLE_WORD_BOUNDARIES = 'remove-double-word-boundaries'


def process_command(command: CommandStrings, config_dict: dict):

    if command is CommandStrings.ADD:
        if not config_dict['flags']['only words']:
            pronunciation_dict = read_pronunciation_dict(
                config_dict['pronunciation dictionary'])
            add_tiers(config_dict, pronunciation_dict=pronunciation_dict)
    elif command is CommandStrings.CONCATENATE:
        if not config_dict['flags']['only words']:
            pronunciation_dict = read_pronunciation_dict(
                config_dict['pronunciation dictionary'])
            concatenate_wavs(
                config_dict, pronunciation_dict=pronunciation_dict)
        else:
            concatenate_wavs(config_dict)
    elif command is CommandStrings.REMOVE_DOUBLE_WORD_BOUNDARIES:
        if not config_dict['output_dirname']:
            print(
                'Fatal: No output directory for new textgrids specified in config file.')
        remove_empty_intervals_from_textgrids(
            Path(original_dirname), Path(config_dict['output_dirname']))
    elif command is CommandStrings.EXTRACT:
        extract_textgrids(Path(original_dirname), Path(outfilename))
    else:
        print(f"Did not recognise the command {command}. Exiting.")
        exit()
