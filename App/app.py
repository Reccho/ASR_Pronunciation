from flask import Flask, render_template, make_response, request
from flask_cors import CORS, cross_origin #bypassing CORS locally
import os, os.path, sys, stat, subprocess, signal, time, random, base64, uuid
import librosa, librosa.display, wave, contextlib, shutil
import xml.etree.ElementTree as ET #XML tree toolkit
import IPython.display as ipd
import matplotlib.pyplot as plt

LibPath = "/home/nichols/sw_project/lib/"
thisPath = "/home/nichols/sw_project/"
userID = ''

#region XML Library interactions (phrase fetching)
#Search xml file for phrase by id and return text string
def phrase_Get(filename, itemNum):
    tree = ET.parse(LibPath + filename)                                     # Create tree from xml file
    root = tree.getroot()                                                   # Begin at root of the tree
    text = root.find('.//phrase[@id="{value}"]'.format(value=itemNum)).text # Search for matching id, return text
    return text

#Return total number of phrases in xml file
def phrase_Num(filename):
    tree = ET.parse(LibPath + filename)     # Create tree from xml file
    root = tree.getroot()                   # Begin at root of the tree
    return len(root.findall('.//phrase'))   # Find all "phrase" -> return count

#Return .xml files in library directory
def getDatasets(path, ext):
    #Get list of all files and trim non-.xml documents
    return (f for f in os.listdir(path) if f.endswith('.' + ext))

#endregion

#region Shell Commands via Python
#Clear files that begin w/ uuid + spectro.png
def clear_Directory(directory, id):
    print(directory + userID + "*")     #TEST
    cmd1 = "rm " + directory + id + "*"     
    cmd2 = "rm " + directory + "spectro.png"
    subprocess.run(cmd1, shell=True)
    subprocess.run(cmd2, shell=True)
    return

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

#endregion

#Create Spectrogram
def Spectro(audioFile, imageFile):
    plt.figure(figsize=(15,4))
    data1,sample_rate1 = librosa.load(audioFile, sr=22050, mono=True, offset=0.0, duration=50, res_type='kaiser_best')
    #librosa.display.waveplot(data1,sr=sample_rate1, max_points=50000.0, x_axis='time', offset=0.0, max_sr=1000)
    fig = plt.Figure()          # create spectrogram figure
    #plt.draw()
    X = librosa.stft(data1)
    Xdb = librosa.amplitude_to_db(abs(X))
    plt.figure(figsize=(14, 5))
    librosa.display.specshow(Xdb, sr=sample_rate1, x_axis='time', y_axis='hz')
    plt.colorbar()

    plt.savefig(imageFile)      # save spectrogram to image file
    os.chmod(imageFile, 0o755)  # O-RWX, G-RX, U-RX
    #plt.show()
    plt.close()

#Return duration of audio file 'filename'
def audio_Duration(filename):
    with contextlib.closing(wave.open(filename,'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)
    return duration

#Reformat audio via ffmpeg
def audio_Reformat(input, output):
    cmd = "ffmpeg -y -i " + input + " -ar 16000 -ac 1 " + output
    subprocess.run(cmd, shell=True)
    return
    
#Prepare the dataset to be fed to ASR
def prep_Dataset(filename, duration, text):
    #DS = open(thisPath + 'dataset/dataset.json','w')
    DS = open(thisPath + 'temp/' + userID + '_dataset.json','w')
    contents = '{"audio_filename": "' + filename + '", "duration": ' + str(duration) + ', "text": "' + text + '"}'
    DS.write(contents)
    DS.close()
    return



#app._static_folder = os.path.abspath("static/")
app = Flask(__name__, static_folder="./static/")
CORS(app)

@app.route('/')
def index():
    global userID
    userID = uuid.uuid4().hex
    print('ID: ' + userID)  #TEST
    return render_template('index.html')

@app.route('/Library', methods=['POST']) #ajax uses GET by def.
def query():
    action = request.form.get('action', '') # default '' if no "action" data
    if action == "numPhrase":   # Number of phrases in dataset
        idD = request.form['idDataset'] # Extract dataset ID
        return str(phrase_Num(idD))     # Return # of phrases in that dataset
    elif action == "getPhrase": # get phrase --> return text
        idP = request.form['idPhrase']  # Extract phrase ID
        idD = request.form['idDataset'] # Extract dataset ID
        phrase = phrase_Get(idD, idP)   # Find phrase (by id) in dataset
        return phrase                   # return string
    elif action == "getDatasets":   # Get available datasets
        files = getDatasets(LibPath, "xml") # Get list of .xml files in library
        filesStr = " "                      # Delimiter
        return (filesStr.join(files))       # Return list of library files
    return ":)" # Default (probably not needed)

@app.route('/Store_Phrase', methods=['POST']) #ajax uses GET by def.
def storePhrase():    # write Phrase to sample.txt
    sampleFile = thisPath + 'temp/' + userID + '_sample.txt'  # Path for sample.txt
    phrase = request.form['text']       # Extract phrase string
    storeTxt = open(sampleFile,'w')     # Create file to hold phrase
    storeTxt.write(phrase)              # Write phrase to file
    storeTxt.close()                    # Close file writing
    os.chmod(sampleFile, 0o755)         # O-RWX, G-RX, U-RX
    return "Phrase -> 'sample.txt'"     # "confirmation" message

@app.route('/Store_Audio', methods=['POST']) #ajax uses GET by def.
def storeAudio():    # write Audio to input.wav, assemble dataset for ASR, create spectrogram
    datasetFile = thisPath + 'temp/' + userID + '_sample.wav'   # Path for sample.wav
    sampleFile = thisPath + 'temp/' + userID + '_sample.txt'    # Path for sample.txt
    audioFile = thisPath + 'temp/' + userID + '_input.wav'      # Path for input.wav
    
    f = open(audioFile, 'wb')   # create file for input
    f.write(request.data)       # write audio to file
    f.close()                   # close file

    phrase_file = open(sampleFile, "r") # open phrase text file
    phrase = phrase_file.read()         # read phrase text string
    phrase_file.close()                 # close file
    
    audio_Reformat(audioFile, datasetFile)      # Reformat audio
    duration = audio_Duration(datasetFile)      # Get duration of audio
    prep_Dataset(datasetFile, duration, phrase) # Create dataset.json
    os.chmod(datasetFile, 0o755)                # O-RWX, G-RX, U-RX
    
    Spectro(audioFile, thisPath + 'temp/spectro.png')
    with open(thisPath + "temp/spectro.png", "rb") as png:
        image_binary = png.read()
        response = make_response(base64.b64encode(image_binary))
        response.headers.set('Content-Type', 'image/gif')
        response.headers.set('Content-Disposition', 'attachment', filename='image.gif')
    return response

@app.route('/Grade', methods=['POST']) #ajax uses GET by def.
def grade():    # Read results file & return strings
    resultsFile = '/home/nichols/sw_project/temp/' + userID + '_graded.txt'
    
    if os.path.exists(resultsFile): 
        with open(resultsFile) as my_file:
            graded = my_file.readlines()
        transcript = graded[0]
        phonemes = graded[1]
        score = graded[2]
        return (transcript + '\n' + phonemes + '\n' + score)
    else:
        return ('XXX')

@app.route('/Clear', methods=['POST']) #ajax uses GET by def.
def Clear():    # clear /temp/ and /dataset
    Temp_dir = thisPath + 'temp'
    clear_Directory(thisPath + 'temp/', userID)
    return("cleared.")

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
