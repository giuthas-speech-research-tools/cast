
from contextlib import closing
from pathlib import Path

import numpy as np
import scipy.io.wavfile as sio_wavfile


def dat_to_wav(datpath: Path, wavpath: Path):
    with closing(open(datpath, 'r')) as dat_file:
        # Matlab version does a test here to decide if the
        # recording is from Labview or RASL 1.0.
        # We don't. We just blindly assume RASL 1.0
        raw_data = dat_file.read_bytes()
        data = np.frombuffer(raw_data, dtype='float')
        diffData = data[1:]-data[0]
        threshold = 0.0001
        numberOfChannels = np.median(
            np.diff(np.nonzero(np.abs(diffData) < threshold)))
        numberOfChannels = int(numberOfChannels)
        print(numberOfChannels)
        if len(data) % numberOfChannels == 0:
            data.shape = [int(len(data)/numberOfChannels), 
                            numberOfChannels]

        print(data.shape)

        difference = np.diff(np.flipud(data[:,3]))
        idx = np.nonzero(difference >= 2)[0]
        idx = len(data[:,3]) - idx + 1
        data = data[:idx, :]

        # Define the DAT variables
        temp = np.diff(np.nonzero(data[:,0]>=1))/np.diff(data(np.nonzero(data[:,0]>=1)))
        sampling_rate = np.round(np.median(temp))
        if sampling_rate != 48000:
            print(f'Calculated sampling rate {sampling_rate} is not equal to 48kHz.')
            sampling_rate = 48000
        data = data/np.repmat(np.max(np.abs(data)), data.shape[0],1)
        
        channel = 2-1
        sound = data[:,channel]
        sound = sound/np.max(np.abs(sound))*0.99

        with closing(open(wavpath, 'w')) as wav_file:
            sio_wavfile.write(wav_file, sampling_rate, sound)
