
from contextlib import closing
from pathlib import Path

def dat_to_wav(datpath):
    with closing(open(datpath, 'r')) as datfile:
        dat = datfile.read()