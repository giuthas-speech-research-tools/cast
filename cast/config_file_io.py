
from contextlib import closing
import csv
from pathlib import Path
import sys
from typing import Dict, List

import strictyaml

def read_config_file(filepath: Path=None) -> Dict:
    """
    Read the config file from filepath.
    
    If filepath is None, read from the default file 'cast_config.yml'.
    In both cases if the file does not exist, report this and exit.
    """
    if filepath is None:
        filepath = Path('cast_config.yml')

    if filepath.is_file():
        with closing(open(filepath, 'r')) as yaml_file:
            config_dict = strictyaml.load(yaml_file.read())
    else:
        print(f"Didn't find {filepath}. Exiting.".format(str(filepath)))
        sys.exit()
    return config_dict.data


def read_exclusion_list(filepath: Path) -> Dict:
    """
    Read the exclusion list from filepath.
    
    If no exclusion list file is present, return an empty array
    after warning the user.
    """
    if filepath.is_file():
        with closing(open(filepath, 'r')) as yaml_file:
            exclusion_dict = strictyaml.load(yaml_file.read())
    else:
        exclusion_dict = {}
        print(f"Did not find the exclusion list at {filepath}. Proceeding anyhow.".format( 
                str(filepath)))
    return exclusion_dict.data


def read_na_list(dirpath: Path) -> List:
    """
    Read the old style exclusion list from na_list.txt.
    
    If no exclusion list file is present, return an empty array
    after warning the user.
    """
    na_file = dirpath.joinpath('na_list.txt')
    if na_file.is_file():
        na_list = [line.rstrip('\n') for line in open(na_file)]
    else:
        na_list = []
        print("Didn't find na_list.txt. Proceeding anyhow.")
    return na_list


def read_pronunciation_dict(filepath: Path) -> Dict:
    """
    Read the pronuciation dictionary and return it as a dict.

    The file is assumed to be in tab separated format and to 
    contain one word on each line followed by the X-SAMPA transcription
    of the expected pronunciation (phonological transcription).

    Returns a dict where each entry is a list of phonomes.
    """
    pronunciation_dict = {}
    if filepath.is_file():
        with closing(open(filepath, 'r')) as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            pronunciation_dict = {row[0]: list(filter(None, row[1:])) for row in reader}
        return pronunciation_dict
    else:
        print(f"Didn't find {pronunciation_dict}. Exiting.".format(pronunciation_dict))
        sys.exit()
