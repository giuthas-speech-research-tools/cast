
from contextlib import closing
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import scipy.io.wavfile as sio_wavfile


def dat_to_wav(datpath: Path, wavpath: Path):
    with closing(open(datpath, 'rb')) as dat_file:
        # Matlab version does a test here to decide if the
        # recording is from Labview or RASL 1.0.
        # We don't. We just blindly assume RASL 1.0
        raw_data = dat_file.read()
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

        # The commented out section below tries to replicate the batchDAT2WAV 
        # behaviour but something makes difference 1D when it should be 2D.
        # Since we are for the moment dealing with a steady data source, 
        # we just hardcode the variables instead.

        # print(data.shape)
        # print(data[:8,:])
        
        # difference = np.diff(np.flipud(data[:,0]))

        # print(np.flipud(data[:,3]).shape)
        # plt.plot(data[:,3])
        # plt.show()

        # idx = np.nonzero(difference >= 2)#[0]
        # idx = len(data[:,3]) - idx + 1
        # data = data[:idx, :]

        # # Define the DAT variables
        # temp = np.diff(np.nonzero(data[:,0]>=1))/np.diff(data(np.nonzero(data[:,0]>=1)))
        # sampling_rate = np.round(np.median(temp))
        # if sampling_rate != 48000:
        #     print(f'Calculated sampling rate {sampling_rate} is not equal to 48kHz.')
        #     sampling_rate = 48000
        # data = data/np.repmat(np.max(np.abs(data)), data.shape[0],1)
        
        channel = 1 # second channel
        sampling_rate = 48000
        sound = data[:,channel]
        sound = sound/np.max(np.abs(sound))*0.99

        with closing(open(wavpath, 'wb')) as wav_file:
            sio_wavfile.write(wav_file, sampling_rate, sound)
