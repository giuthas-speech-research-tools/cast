from contextlib import closing
from pathlib import Path

def add_prompt_info(table: list, exclusion_list: list) -> None:
    """
    Check for existence of prompts and add the prompt to table.

    If the prompt file does not exist, set the flag 'excluded' to True.

    Works in place, so does not return anything.
    """
    for entry in table:
        if not entry['prompt_path'].is_file():
            filename = entry['filename']
            print(f'Excluding {filename}. Recording has no prompt file.')
            entry['excluded'] = True
        else:
            with closing(open(entry['prompt_path'], 'r')) as prompt_file:
                prompt = prompt_file.readline().strip()

                # The first condition sees if the whole prompt is excluded, 
                # the second condition checks if any parts of the prompt 
                # match exclucion criteria (for example excluding 'foobar ...' 
                # based on 'foobar').
                if (prompt in exclusion_list['prompts'] or
                    [element for element in exclusion_list['parts of prompts'] if(element in prompt)]):
                    print(f'Excluding {filename}. Prompt: {prompt} matches exclusion list.')
                    entry['excluded'] = True
                entry['word'] = prompt


def check_and_load_aaa_meta(speaker_id: str, directory: Path, test: bool) -> list:
    # Since we are concerned with audio annotation, wav files 
    # determine the name list for all other files.
    wav_files = sorted(directory.glob('*.wav'))
    # for test runs do only first ten files:
    if test:
        wav_files = wav_files[:10]

    if(len(wav_files) < 1):
        print(f"Didn't find any sound files to concatanate in {directory}.")
        exit()

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
                'prompt_path': wavfile.with_suffix('.txt'),
                'ultra_path': wavfile.with_suffix('.ult'),
                'id':wavfile.stem,
                'speaker':speaker_id, 
                'sliceBegin':'n/a',
                'begin':'n/a', 
                'end':'n/a', 
                'word':'n/a'} 
            for wavfile in wav_files]

    for entry in table: 
        filename = entry['filename']
        if not entry['ultra_path'].is_file():
            print(f'Excluding {filename}. Recording has no ultrasound file.')
            entry['excluded'] = True
        
    add_prompt_info(table)

    return table
