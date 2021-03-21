from flask import Flask, request    #Flask for post requests
from flask_cors import CORS         #bypassing CORS locally
import xml.etree.ElementTree as ET     #XML tree toolkit
import os, os.path, subprocess, time     

#Search xml file for phrase by id and return text string
def phrase_Get(itemNum):
    #print("getting phrase: " + itemNum) #TEST
    tree = ET.parse(xmlpath)   # Create tree from xml file
    root = tree.getroot()                                                           # Start at root
    text = root.find('.//phrase[@id="{value}"]'.format(value=itemNum)).text         # Search for matching id, pull text
    return text

#Return total number of phrases in xml file
def phrase_Num():
    tree = ET.parse(xmlpath)   # Create tree from xml file
    root = tree.getroot()
    return len(root.findall('.//phrase'))

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

#Run the ASR on 'dataset.json', return score
def Grade(dataset):
    '''
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
    args = parser.parse_args(["--dataset", "dataset.json", "--asr_model", "QuartzNet15x5Base-En"])
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
    '''
    return 8




# create the Flask app
app = Flask(__name__)
CORS(app)

@app.route('/Action', methods=['POST']) #ajax uses GET by def.
def query():
    if request.form['action'] == "grade": # get audio --> return grade
        return 1
    elif request.form['action'] == "numPhrase": # get phrase number --> return string
        number = phrase_Num()
        return number
        #return 2
    elif request.form['action'] == "getPhrase": # get phrase number --> return string
        id = request.form['idPhrase']
        phrase = phrase_Get(id)
        return phrase
        #return 3
    elif request.form['action'] == "getDataset": # get dataset name --> return dataset title, open xml tree
        pass
    return ":)"

if __name__ == '__main__':
    # run app in debug mode on port 5000
    app.run(debug=True, port=5000)
