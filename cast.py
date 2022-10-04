
import sys
import time

from cast import concatenate_wavs

def main(args):
    outfilename = args.pop()
    original_dirname = args.pop()
    speaker_id = args.pop()
    if args:
        if '--test' in args:
            test = True
        else:
            test = False
        if '--beep' in args:
            detect_beep = True
        else:
            detect_beep = False
        concatenate_wavs(speaker_id, original_dirname, outfilename, 
            test = test, detect_beep = detect_beep)
    else: 
        concatenate_wavs(speaker_id, original_dirname, 
            outfilename)


if (len(sys.argv) not in [5, 6]):
    print("\nconcatenate.py")
    print("\tusage: concatenate.py [--test] [--beep] speaker_id original_directory outputfilename")
    print("\n\tConcatenates wav files and creates a corresponding TextGrid.")
    print("\t--test runs the code on only first ten files")
    print("\t--beep finds a 1kHz 50ms beep (go-signal), marks it, and starts segmentation after it.")
    print("\tWrites a huge wav-file.")
    print("\tAlso writes a richer metafile to be read by extract.py or similar.")
    print("\tAlso writes a huge textgrid with phonological transcriptions of the words.")
    sys.exit(0)


if (__name__ == '__main__'):
    t = time.time()
    main(sys.argv[1:])
    print('Elapsed time {elapsed_time}'.format(elapsed_time = (time.time() - t)))