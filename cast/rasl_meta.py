import sys
from datetime import datetime
from pathlib import Path, PureWindowsPath

import scipy.io

from cast.rasl_dat_to_wav import dat_to_wav


def convert_dats_to_wav(table: dict) -> None:
    print(f"Looking for DAT files and trying to convert them to WAV.")
    for entry in table:
        if entry['dat_path'].is_file():
            dat_to_wav(entry['dat_path'], entry['wav_path'])
        else:
            print(f"Dat file {entry['dat_path']} does not exist. Skipping.")
            continue

def check_and_load_rasl_meta(speaker_id: str, directory: Path, 
                            test: bool) -> list[dict]:
    """
    Read a RASL .mat file and return relevant contents as a dict.
    """
    wav_dir = directory / "WAV"

    note_dir = directory / "NOTES"
    if not note_dir.is_dir():
        note_dir = directory / "Notes"
    if not note_dir.is_dir():
        note_dir = directory / "notes"
    if not note_dir.is_dir():
        print(f"Notes dir {note_dir} does not exist. Exiting.")
        sys.exit()

    possible_notes = sorted(note_dir.glob('officialNotes*.mat'))
    if not possible_notes:
        print(f"Found no notes in {note_dir}. Exiting.")
        sys.exit()
    mat_file = possible_notes[0]
 
    mat = scipy.io.loadmat(str(mat_file), squeeze_me=True)
    if not mat:
        print(f"Official notes at {mat_file} seems to be empty. Exiting.")
        sys.exit()

    table = []
    for element in mat['officialNotes']:
        # Apparently squeeze_me=True is a bit too strident and
        # somehow looses the shape of the most interesting level
        # in the loadmat call. Not using it is not a good idea
        # though so we do this:
        element = element.item()
        if len(element) > 5:
            # We try this two ways, because at least once filename
            # and date fields were in reversed order inside the
            # .mat file.
            try:
                date_and_time = datetime.strptime(
                    element[4], "%d-%b-%Y %H:%M:%S")
                dat_name = PureWindowsPath(element[5])
            except ValueError:
                dat_name = PureWindowsPath(element[4])
                date_and_time = datetime.strptime(
                    element[5], "%d-%b-%Y %H:%M:%S")

            dat_name = dat_name.name
            dat_path = directory/"DAT"/dat_name
            dat_path = dat_path.with_suffix('.dat')

            wav_path = (wav_dir/dat_path.stem).with_suffix('.wav')

            meta_token = {
                'excluded': False,
                'trial_number': element[0],
                'filename': dat_path.stem,
                'dat_filename': dat_path.name,
                'dat_path': dat_path,
                'wav_path': wav_path,
                'id':dat_path.stem,
                'speaker':speaker_id, 
                'sliceBegin':'n/a',
                'begin':'n/a', 
                'end':'n/a', 
                'date_and_time': date_and_time,
                'prompt': element[1]
            }
            table.append(meta_token)

    wav_files = sorted(wav_dir.glob('*.wav'))
    if(len(wav_files) < 1):
        print(f"Didn't find any sound files to concatanate in {directory}.")
        if not wav_dir.is_dir():
            wav_dir.mkdir()
        convert_dats_to_wav(table)

    # for test runs do only first ten files:
    if test and len(table) >= 10:
        table = table[:10]

    return table

