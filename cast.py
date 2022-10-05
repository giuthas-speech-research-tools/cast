
import sys
import time

from cast import concatenate_wavs, read_config_file, read_pronunciation_dict

def main(args):
    outfilename = args.pop()
    original_dirname = args.pop()
    speaker_id = args.pop()
 
    test = False
    detect_beep = False
    only_words = False
    if '--test' in args:
        test = True
    if '--beep' in args:
        detect_beep = True
    if '--only_words' in args:
        only_words = True
 
    config_dict = read_config_file()

    if not only_words:
        pronunciation_dict = read_pronunciation_dict(config_dict['pronunciation_dictionary'])
        concatenate_wavs(speaker_id, original_dirname, outfilename, config_dict, 
            pronunciation_dict=pronunciation_dict, test=test, detect_beep=detect_beep)
    else:
        concatenate_wavs(speaker_id, original_dirname, outfilename, config_dict, 
            test=test, detect_beep=detect_beep)


if (len(sys.argv) not in [5, 6, 7]):
    print("\ncast.py")
    print("\tusage: cast.py [--test] [--beep] speaker_id original_directory outputfilename")
    print("\n\tConcatenates wav files and creates a corresponding TextGrid.")
    print("\t--test runs the code on only first ten files")
    print("\t--beep finds a 1kHz 50ms beep (go-signal), marks it, and starts segmentation after it.")
    print("\tWrites a huge wav-file.")
    print("\tAlso writes a richer metafile to be read by extract.py or similar.")
    print("\tAlso writes a huge textgrid with phonological transcriptions of the words.")
    sys.exit(0)


if (__name__ == '__main__'):
    start_time = time.perf_counter()
    main(sys.argv[1:])
    elapsed_time = time.perf_counter() - start_time
    print(f'Elapsed time was {elapsed_time}.')