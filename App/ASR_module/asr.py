import os, os.path, sys, time, subprocess, json
import torch
from argparse import ArgumentParser
from nemo.collections.asr.metrics.wer import WER, word_error_rate
from nemo.collections.asr.models import EncDecCTCModel
from nemo.utils import logging

#Phonetic labels used by the ASR model
LABELS = [" ", "a", "aɪ", "aɪə", "aɪɚ", "aʊ", "b", "d", "dʒ", "eɪ", "f", "h", 
          "i", "iə", "iː", "j", "k", "l", "m", "n", "n̩", "oʊ", "oː", "oːɹ", 
          "õ", "p", "r", "s", "t", "tʃ", "uː", "v", "w", "x", "z", "æ", "ç", 
          "ð", "ŋ", "ɐ", "ɑː", "ɑːɹ", "ɑ̃", "ɔ", "ɔɪ", "ɔː", "ɔːɹ", "ɔ̃", "ɕ", 
          "ə", "əl", "ɚ", "ɛ", "ɛɹ", "ɜː", "ɡ", "ɡʲ", "ɪ", "ɪɹ", "ɬ", "ɹ", "ɾ", 
          "ʃ", "ʊ", "ʊɹ", "ʌ", "ʒ", "ʔ", "β", "θ", "ᵻ" ]

#Paths and Model names
datasetPath = os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + '/temp/'
#quartz_base_Path ='/home/nichols/.cache/torch/NeMo/NeMo_1.0.0rc2/QuartzNet15x5Base-En/2b066be39e9294d7100fb176ec817722/QuartzNet15x5Base-En.nemo'
#quartz_phon_Path = '/home/nichols/sw_project/ASR_module/asr_models/quartz_phon/quartz_phon.nemo'
quartz_base_Path = './asr_models/torch/NeMo/NeMo_1.0.0rc2/QuartzNet15x5Base-En/2b066be39e9294d7100fb176ec817722/QuartzNet15x5Base-En.nemo'
quartz_phon_Path = './asr_models/quartz_phon/quartz_phone.nemo'
#The module files are too large to upload to github, but /asr_models/ belongs to this directory and contains the instances of the neural networks.

model_Quartz_base = 'QuartzNet15x5Base-En'  #Model based on words
model_Quartz_phon = 'quartz_phon'           #...based on phonemes

#Set ASR model to be used:
model_Selected = model_Quartz_phon
model_Path = quartz_phon_Path
mtime = 0.0     # Start modified-time at 0



#Run the ASR on 'dataset.json', return score
def ASR_Grade(dataset, id, key):
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
        default=model_Selected,
        required=True,
        help=f'Pass: {model_Selected}',
    )
    parser.add_argument("--dataset", type=str, required=True, help="path to evaluation data")
    parser.add_argument("--batch_size", type=int, default=4)
    parser.add_argument("--wer_tolerance", type=float, default=1.0, help="used by test")
    parser.add_argument(
        "--normalize_text",
        default=False, # False <- we're using phonetic references
        type=bool,
        help="Normalize transcripts or not. Set to False for non-English.",
    )
    args = parser.parse_args(["--dataset", dataset, "--asr_model", model_Selected])
    torch.set_grad_enabled(False)

    # Instantiate Jasper/QuartzNet models with the EncDecCTCModel class.
    asr_model = EncDecCTCModel.restore_from(model_Path)

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
            reference = key
            #reference = "".join([labels_map[c] for c in test_batch[2][batch_ind].cpu().detach().numpy()])  #debug
            print(reference) #debug
            references.append(reference)
        del test_batch
    wer_value = word_error_rate(hypotheses=hypotheses, references=references) #cer=True

    REC = '.'
    REF = '.'
    for h, r in zip(hypotheses, references):
        print("Recognized:\t{}\nReference:\t{}\n".format(h, r))
        REC = h
        REF = r
    logging.info(f"Got PER of {wer_value}. Tolerance was {args.wer_tolerance}")

    #Score Calculation, phoneme conversion
    # divide wer_value by wer_tolerance to get the ratio of correctness (and round it)
    # then multiply by 100 to get a value above 0
    # since this give the "% wrong", subtract from 100 to get "% correct"
    # this gives a positive grade to show return to the user
    score = 100.00 - (round((wer_value / args.wer_tolerance), 4) * 100)
    if score < 0.0:
        score = 0.0
    print(score)

    #Result file creation, to be accessed by JS via 'app.py'
    Results = open(datasetPath + id + '_graded.txt','w')
    Results.write(REC + '\n' + REF + '\n' + str(score))
    Results.close()
    return score



#MAIN
while True:
    time.sleep(1.0)
    for file in os.listdir(datasetPath):
        try:
            if "dataset.json" in file:
                newtime = os.path.getmtime(datasetPath + file)
                if newtime <= mtime: #file is not fresh
                    continue
                else:
                    mtime = newtime #update modified-time checkpoint
                    print('Detected fresh dataset.json...') #debug
                    try:
                        arr = file.split('_', 1) #debug, get uuid
                        print(arr[0])   #debug, show uuid in use
                        
                        with open(datasetPath + file) as f:
                            data = json.load(f)

                        ASR_Grade(datasetPath + file, arr[0], data["text"])
                    except:
                        continue
            else:
                continue
        except: print("File Error.")
