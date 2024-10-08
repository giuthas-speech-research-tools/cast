
from enum import Enum
from pathlib import Path
import sys

from .aaa_meta import check_and_load_aaa_meta
from .rasl_meta import check_and_load_rasl_meta


class Datasource(Enum):
    """
    Data sources SATKIT can handle.

    Used in saving and loading to identify the data source in config, as well as
    in meta and skip the step of trying to figure the data source out from the
    type of files present.
    """
    AAA = "AAA"
    # EVA = "EVA"
    RASL = "RASL"
    CSV = "csv"


def get_token_list(config_dict: dict, directory: Path) -> dict:
    speaker_id = config_dict['speaker id']
    test = config_dict['test']

    data_source = config_dict['data source']
    if data_source is Datasource.AAA:
        table = check_and_load_aaa_meta(speaker_id, directory, test)
    elif data_source is Datasource.RASL:
        table = check_and_load_rasl_meta(speaker_id, directory, test)
    elif data_source is Datasource.CSV:
        # table = check_and_load_csv_meta(
        #     speaker_id, directory, test, csv_meta_file)
        # This was supposed to be in used in the palatalisation project.
        print(f"Unsupported data source: {data_source}. Exiting")
        sys.exit()
    else:
        print(f"Unknown data source: {data_source}. Exiting.")
        sys.exit()

    return table
