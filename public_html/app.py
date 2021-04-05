from flask import Flask, render_template, request
from flask_cors import CORS, cross_origin #bypassing CORS locally
import xml.etree.ElementTree as ET     #XML tree toolkit
import os, os.path, subprocess, time, wave, contextlib, librosa, librosa.display
import IPython.display as ipd
import matplotlib.pyplot as plt
import torch
from argparse import ArgumentParser
from nemo.collections.asr.metrics.wer import WER, word_error_rate
from nemo.collections.asr.models import EncDecCTCModel
from nemo.utils import logging

LibPath = "./lib/"

#Search xml file for phrase by id and return text string
def phrase_Get(filename, itemNum):
    tree = ET.parse(LibPath + filename)   # Create tree from xml file
    print(LibPath + filename)
    root = tree.getroot()                                                           # Start at root
    text = root.find('.//phrase[@id="{value}"]'.format(value=itemNum)).text         # Search for matching id, pull text
    return text

#Return total number of phrases in xml file
def phrase_Num(filename):
    tree = ET.parse(LibPath + filename)   # Create tree from xml file
    root = tree.getroot()
    return len(root.findall('.//phrase'))

#Return .xml files in library directory
def getDatasets(path, ext):
    return (f for f in os.listdir(path) if f.endswith('.' + ext))

#Create Spectrogram
def Spectro(filename):
    plt.figure(figsize=(15,4))
    data1,sample_rate1 = librosa.load(filename, sr=22050, mono=True, offset=0.0, duration=50, res_type='kaiser_best')
    librosa.display.waveplot(data1,sr=sample_rate1, max_points=50000.0, x_axis='time', offset=0.0, max_sr=1000)
    fig = plt.Figure()          #create spectrogram figure
    plt.draw()
    plt.savefig('./temp/spectro.png')  #save spectrogram to image file
    #plt.show()

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

#Run 'soxi -D' on file "filename"
def sox_i(filename):
    cmd = "soxi -D " + filename
    sub = subprocess.Popen(cmd, 
        shell=True, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE, 
        universal_newlines=True)
    sox = sub.communicate()[0]
    return(sox)

#Run 'pwd -P' on file "filename"
def pwd_P(filename):
    cmd = "pwd -P " + filename
    sub = subprocess.Popen(cmd, 
        shell=True, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE, 
        #universal_newlines=True
        )
    sox = sub.communicate()[0]
    return(sox.decode().replace('\n', '') + "/" + filename)

#Return duration of audio file 'filename'
def audio_Duration(filename):
    with contextlib.closing(wave.open(filename,'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)
        #print(duration)
    return duration

#Run 'ffmpeg -i "input_file.mp3" -ar 16000 -ac 1 "output.wav"' on file
def audio_Reformat(input, output):
    cmd = "ffmpeg -i " + input + " -ar 16000 -ac 1 " + output
    subprocess.Popen(cmd, 
        shell=True, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE, 
        #universal_newlines=True
        )
    return

#Prepare the dataset to be fed to ASR
def prep_Dataset(filename, duration, text):
	contents = "{\"audio_filename\": \"" + filename + "\", \"duration\": " + str(duration) + ", \"text\": \"" + text + "\"}"
	cmd = "echo " + contents + " >" + "./" + "dataset.json"
	subprocess.Popen(cmd, 
        shell=True, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE, 
        universal_newlines=True)
	return

#Run the ASR on 'dataset.json', return score
def Grade(dataset):
    #Running the ASR
    parser = ArgumentParser()
    parser.add_argument(
        "--asr_model", type=str, default="QuartzNet15x5Base-En", required=True, help="Pass: 'QuartzNet15x5Base-En'",
    )
    parser.add_argument("--dataset", type=str, required=True, help="path to evaluation data")
    parser.add_argument("--batch_size", type=int, default=4)
    parser.add_argument("--wer_tolerance", type=float, default=1.0, help="used by test")
    parser.add_argument(
        "--normalize_text", default=True, type=bool, help="Normalize transcripts or not. Set to False for non-English."
    )
    #args = parser.parse_args(["--dataset", "dataset.json", "--asr_model", "QuartzNet15x5Base-En"])
    args = parser.parse_args(["--dataset", dataset, "--asr_model", "QuartzNet15x5Base-En"])
    #torch.set_grad_enabled(False)

    if args.asr_model.endswith('.nemo'):
        logging.info(f"Using local ASR model from {args.asr_model}")
        asr_model = EncDecCTCModel.restore_from(restore_path=args.asr_model)
    else:
        logging.info(f"Using NGC cloud ASR model {args.asr_model}")
        asr_model = EncDecCTCModel.from_pretrained(model_name=args.asr_model)
    asr_model.setup_test_data(
        test_data_config={
            'sample_rate': 16000,
            'manifest_filepath': args.dataset,
            'labels': asr_model.decoder.vocabulary,
            'batch_size': args.batch_size,
            'normalize_transcripts': args.normalize_text,
        }
    )
    if can_gpu:
        asr_model = asr_model.cuda()
    asr_model.eval()
    labels_map = dict([(i, asr_model.decoder.vocabulary[i]) for i in range(len(asr_model.decoder.vocabulary))])
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
        hypotheses += wer.ctc_decoder_predictions_tensor(greedy_predictions)
        for batch_ind in range(greedy_predictions.shape[0]):
            reference = ''.join([labels_map[c] for c in test_batch[2][batch_ind].cpu().detach().numpy()])
            references.append(reference)
        del test_batch
    wer_value = word_error_rate(hypotheses=hypotheses, references=references)
    
    for h, r in zip(hypotheses, references):
      print("Recognized:\t{}\nReference:\t{}\n".format(h, r))

    logging.info(f'Got WER of {wer_value}. Tolerance was {args.wer_tolerance}')

    score = (round((wer_value / args.wer_tolerance), 4) * 100)
    return score


app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/Grade', methods=['POST']) #ajax uses GET by def.
def grade():    # get audio --> return grade
    #phrase = request.form['phrase']
    phrase_file = open("./temp/sample.txt", "r")
    phrase = phrase_file.read()
    phrase_file.close()
    #
    f = open('./temp/input.wav', 'wb')   #create file for input
    f.write(request.data)           #write audio to file
    f.close()                       #
    #
    audio_Reformat("./temp/input.wav", "./temp/sample.wav")   # Reformat audio w/ ffmpeg
    dur = audio_Duration("./temp/sample.wav")       # Get duration of sample
    prep_Dataset("./temp/sample.wav", dur, phrase)
    Spectro("./temp/input.wav")
    #
    # pass to ASR
    #
    return "File written."

@app.route('/Library', methods=['POST']) #ajax uses GET by def.
def query():
    action = request.form.get('action', '')     # default '' if no "action" data

    if action == "numPhrase":         # get phrase number --> return string
        idD = request.form['idDataset']
        return str(phrase_Num(idD))
    elif action == "getPhrase":         # get phrase number --> return string
        idP = request.form['idPhrase']
        idD = request.form['idDataset']
        phrase = phrase_Get(idD, idP)
        return phrase
    elif action == "getDatasets":       # get dataset name --> return dataset title, open xml tree
        files = getDatasets("./lib/", "xml")
        filesStr = " "
        return (filesStr.join(files))
    return ":)"

@app.route('/Store', methods=['POST']) #ajax uses GET by def.
def storeSam():    # write Phrase to sample.txt
    phrase = request.form['text']
    print(phrase)
    storeTxt = open(r'./temp/sample.txt','w')
    storeTxt.write(phrase)
    storeTxt.close()
    return "Phrase -> 'sample.txt'"

if __name__ == '__main__':
    app.run(debug=True)
