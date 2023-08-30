from contextlib import closing
from csv import DictReader
from pathlib import Path


def add_prompt_info(table: dict, csv_meta_file: Path):
    meta_dict = {}
    with closing(open(csv_meta_file, 'r')) as meta_file:
        reader = DictReader(meta_file)
        for row in reader:
            meta_dict[row['id']] = row['ortho']

    for item in table:
        item['prompt'] = meta_dict[item['token_id']]


def check_and_load_csv_meta(speaker_id: str, directory: Path, 
                            test: bool, csv_meta_file: Path) -> list[dict]:
    # Since we are concerned with audio annotation, wav files 
    # determine the name list for all other files.
    wav_files = sorted(directory.glob('*.wav'))
    if(len(wav_files) < 1):
        print(f"Didn't find any sound files to concatanate in {directory}.")
        exit()

    # for test runs do only first ten files:
    if test and len(wav_files) >= 10:
        wav_files = wav_files[:10]


    prompt_files = sorted(directory.glob('*.txt')) 
    if(len(prompt_files) < 1):
        print("Didn't find any prompt files in {dirname}.")
        exit()

    # initialise table with the speaker_id and name repeated, wav_file name
    # from the list, and other fields empty
    table = [{
                'excluded': False,
                'filename': wavfile.stem,
                'wav_path': wavfile,
                'token_id': wavfile.stem[6:10].replace('_', '.'),
                'prompt_path': None,
                'ultra_path': None,
                'id':wavfile.stem,
                'speaker':speaker_id, 
                'sliceBegin':'n/a',
                'begin':'n/a', 
                'end':'n/a', 
                'prompt':'n/a'} 
            for wavfile in wav_files]

    add_prompt_info(table, csv_meta_file)

    return table
