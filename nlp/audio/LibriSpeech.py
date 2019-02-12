# all LibriSpeech files, we download only from 'filter'   
LIBRI_SPEECH_URLS = {
    "train": ["http://www.openslr.org/resources/12/train-clean-100.tar.gz",
              "http://www.openslr.org/resources/12/train-clean-360.tar.gz",
              "http://www.openslr.org/resources/12/train-other-500.tar.gz"],

    "val": ["http://www.openslr.org/resources/12/dev-clean.tar.gz",
            "http://www.openslr.org/resources/12/dev-other.tar.gz"],

    "test_clean": ["http://www.openslr.org/resources/12/test-clean.tar.gz"],
    "test_other": ["http://www.openslr.org/resources/12/test-other.tar.gz"]
}


def run_download_process():
    if not os.path.exists(target_dl_dir):
        os.makedirs(target_dl_dir)
    for split_type, lst_libri_urls in LIBRI_SPEECH_URLS.items():
        split_dir = os.path.join(target_dl_dir, split_type)
        if not os.path.exists(split_dir):
            os.makedirs(split_dir)
        split_wav_dir = os.path.join(split_dir, "wav")
        if not os.path.exists(split_wav_dir):
            os.makedirs(split_wav_dir)
        split_txt_dir = os.path.join(split_dir, "txt")
        if not os.path.exists(split_txt_dir):
            os.makedirs(split_txt_dir)
        extracted_dir = os.path.join(split_dir, "LibriSpeech")
        if os.path.exists(extracted_dir):
            shutil.rmtree(extracted_dir)
        for url in lst_libri_urls:
            # check if we want to dl this file
            dl_flag = False
            for f in files_to_dl:
                if url.find(f) != -1:
                    dl_flag = True
            if not dl_flag:
                print("Skipping url: {}".format(url))
                continue
            filename = url.split("/")[-1]
            target_filename = os.path.join(split_dir, filename)
            if not os.path.exists(target_filename):
                wget.download(url, split_dir)
            print("Unpacking {}...".format(filename))
            tar = tarfile.open(target_filename)
            tar.extractall(split_dir)
            tar.close()
            os.remove(target_filename)
            print("Converting flac files to wav and extracting transcripts...")
            assert os.path.exists(extracted_dir), "Archive {} was not properly uncompressed.".format(filename)
            for root, subdirs, files in tqdm(os.walk(extracted_dir)):
                for f in files:
                    if f.find(".flac") != -1:
                        _process_file(wav_dir=split_wav_dir, txt_dir=split_txt_dir,
                                      base_filename=f, root_dir=root)

            print("Finished {}".format(url))
            shutil.rmtree(extracted_dir)
        if split_type == 'train':  # Prune to min/max duration
            create_manifest(split_dir, 'libri_' + split_type + '_manifest.csv', min_duration, max_duration)
        else:
            create_manifest(split_dir, 'libri_' + split_type + '_manifest.csv')

