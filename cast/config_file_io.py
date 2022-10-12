
import csv
import sys
from contextlib import closing
from pathlib import Path
from typing import Union

from strictyaml import Bool, Float, Map, Str, YAMLError, load


def read_config_file(filepath: Union[Path, str, None]=None) -> dict:
    """
    Read the config file from filepath.
    
    If filepath is None, read from the default file 'cast_config.yml'.
    In both cases if the file does not exist, report this and exit.
    """
    if filepath is None:
        filepath = Path('cast_config.yml')
    elif isinstance(filepath, str):
        filepath = Path(filepath)

    if filepath.is_file():
        with closing(open(filepath, 'r')) as yaml_file:
            schema = Map({
                "data source": Str(), 
                "speaker id": Str(), 
                "data directory": Str(), 
                "outputfilename": Str(), 
                "flags": Map({
                    "detect beep": Bool(),
                    "only words": Bool(),
                    "test": Bool(),
                    "file": Bool(),
                    "utterance": Bool()
                    }),
                "exclusion list": Str(), 
                "pronunciation dictionary": Str(), 
                "word guess": Map({
                    "begin": Float(),
                    "end": Float()
                    })
                })
            try:
                config_dict = load(yaml_file.read(), schema)
            except YAMLError as error:
                print(f"Fatal error in reading {filepath}:")
                print(error)
                sys.exit()
    else:
        print(f"Didn't find {filepath}. Exiting.".format(str(filepath)))
        sys.exit()
    return config_dict.data


def read_exclusion_list(filepath: Path) -> dict:
    """
    Read the exclusion list from filepath.
    
    If no exclusion list file is present, return an empty array
    after warning the user.
    """
    if filepath.is_file():
        with closing(open(filepath, 'r')) as yaml_file:
            yaml = load(yaml_file.read())
            exclusion_dict = yaml.data
    else:
        exclusion_dict = {}
        print(f"Did not find the exclusion list at {filepath}. Proceeding anyhow.")
    return exclusion_dict


def read_na_list(dirpath: Path) -> list[str]:
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


def read_pronunciation_dict(filepath: Union[Path, str]) -> dict:
    """
    Read the pronuciation dictionary and return it as a dict.

    The file is assumed to be in tab separated format and to 
    contain one word on each line followed by the X-SAMPA transcription
    of the expected pronunciation (phonological transcription).

    Returns a dict where each entry is a list of phonomes.
    """
    if isinstance(filepath, str):
        filepath = Path(filepath)

    pronunciation_dict = {}
    if filepath.is_file():
        with closing(open(filepath, 'r')) as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            pronunciation_dict = {row[0]: list(filter(None, row[1:])) 
                                    for row in reader}
        return pronunciation_dict
    else:
        print(f"Didn't find {pronunciation_dict}. Exiting.")
        sys.exit()
