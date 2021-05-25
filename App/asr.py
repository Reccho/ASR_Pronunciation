import os, os.path, sys, time, random, glob, subprocess
import torch
from argparse import ArgumentParser
from nemo.collections.asr.metrics.wer import WER, word_error_rate
from nemo.collections.asr.models import EncDecCTCModel
from nemo.utils import logging

#Phonemize "phrase" to get phonetic representation
def phonemize(phrase):
    cmd = "echo " + phrase + " | phonemize"
    sub = subprocess.Popen(cmd, 
        shell=True, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE, 
        universal_newlines=True)
    key = sub.communicate()[0]
    return key

#Run the ASR on 'dataset.json', return score
def ASR_Grade(dataset, id):
    try:
        from torch.cuda.amp import autocast
    except ImportError:
        from contextlib import contextmanager

        @contextmanager
        def autocast(enabled=None):
            yield

    can_gpu = torch.cuda.is_available()

    parser = ArgumentParser()
    parser.add_argument(
        "--asr_model",
        type=str,
        default="QuartzNet15x5Base-En",
        required=True,
        help="Pass: 'QuartzNet15x5Base-En'",
    )
    parser.add_argument(
        "--dataset", type=str, required=True, help="path to evaluation data"
    )
    parser.add_argument("--batch_size", type=int, default=4)
    parser.add_argument("--wer_tolerance", type=float, default=1.0, help="used by test")
    parser.add_argument(
        "--normalize_text",
        default=True,
        type=bool,
        help="Normalize transcripts or not. Set to False for non-English.",
    )
    # args = parser.parse_args(["--dataset", "dataset.json", "--asr_model", "QuartzNet15x5Base-En"])
    args = parser.parse_args(
        ["--dataset", dataset, "--asr_model", "QuartzNet15x5Base-En"]
    )
    torch.set_grad_enabled(False)

    if args.asr_model.endswith(".nemo"):
        logging.info(f"Using local ASR model from {args.asr_model}")
        asr_model = EncDecCTCModel.restore_from(restore_path=args.asr_model)
    else:
        logging.info(f"Using NGC cloud ASR model {args.asr_model}")
        asr_model = EncDecCTCModel.from_pretrained(model_name=args.asr_model)
    asr_model.setup_test_data(
        test_data_config={
            "sample_rate": 16000,
            "manifest_filepath": args.dataset,
            "labels": asr_model.decoder.vocabulary,
            "batch_size": args.batch_size,
            "normalize_transcripts": args.normalize_text,
        }
    )
    if can_gpu:  # noqa
        asr_model = asr_model.cuda()
    asr_model.eval()
    labels_map = dict(
        [
            (i, asr_model.decoder.vocabulary[i])
            for i in range(len(asr_model.decoder.vocabulary))
        ]
    )
    wer = WER(vocabulary=asr_model.decoder.vocabulary)
    hypotheses = []
    references = []
    for test_batch in asr_model.test_dataloader():
        if can_gpu:
            test_batch = [x.cuda() for x in test_batch]
        with autocast():
            log_probs, encoded_len, greedy_predictions = asr_model(
                input_signal=test_batch[0], input_signal_length=test_batch[1]
            )
        hypotheses = wer.ctc_decoder_predictions_tensor(greedy_predictions)
        for batch_ind in range(greedy_predictions.shape[0]):
            reference = "".join(
                [labels_map[c] for c in test_batch[2][batch_ind].cpu().detach().numpy()]
            )
            references.append(reference)
        del test_batch
    wer_value = word_error_rate(hypotheses=hypotheses, references=references)

    transcript = '.'
    for h, r in zip(hypotheses, references):
        print("Recognized:\t{}\nReference:\t{}\n".format(h, r))
        transcript = h

    logging.info(f"Got WER of {wer_value}. Tolerance was {args.wer_tolerance}")


    #Score Calculation, phoneme conversion
    score = 100.00 - (round((wer_value / args.wer_tolerance), 4) * 100)
    phonemes = phonemize(transcript)

    #RESULT FILE CREATION
    Results = open('/home/nichols/sw_project/temp/' + id + '_graded.txt','w')
    Results.write(transcript + '\n' + phonemes + '\n' + str(score))
    Results.close()
    return score


datasetPath = '/home/nichols/sw_project/temp/'
mtime = 0.0

while True:
    time.sleep(1.0)
    for file in os.listdir(datasetPath):
        if "dataset.json" in file:
            newtime = os.path.getmtime(datasetPath + file)
            if newtime <= mtime:
                continue
            else:
                mtime = newtime
                try:
                    arr = file.split('_', 1)
                    print(arr[0])
                    ASR_Grade(datasetPath + file, arr[0])
                except:
                    continue
        else:
            continue
    '''
    if os.path.exists('/home/nichols/sw_project/dataset/dataset.json') == True:
        newtime = os.path.getmtime('/home/nichols/sw_project/dataset/dataset.json')
        if newtime == mtime:
            continue
        else:
            mtime = newtime
            try:
                print("Dataset changed.")
                #ASR_Grade('/home/nichols/sw_project/dataset/dataset.json')
            except:
                continue
    else:
        continue
    '''
