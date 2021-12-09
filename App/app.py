from flask import Flask, render_template, make_response, request, url_for
from flask_cors import CORS, cross_origin #bypassing CORS locally
import os, os.path, sys, subprocess, base64, stat, signal, time, random
import librosa, librosa.display, wave, contextlib, shutil
import xml.etree.ElementTree as ET #XML tree toolkit
import IPython.display as ipd
import matplotlib.pyplot as plt
from phonemizer import phonemize


if not sys.warnoptions: #Suppress warnings for cleaner output
    import warnings
    warnings.simplefilter("ignore")

#Some oft-used filepaths for easier to read arguments
thisPath = "/home/nichols/sw_project/"      # Directory w/ this program
LibPath = "/home/nichols/sw_project/lib/"   # Directory w/ phrase libraries
tempPath = "/home/nichols/sw_project/temp/" # Directory which holds temp files created by program

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
    cmd1 = "rm " + directory + id + "*"  #Command := "Delete all files in this dir w/ id in beginning of name"
    subprocess.run(cmd1, shell=True)     #Run the 'rm' command
    return

#Reformat audio via ffmpeg
def audio_Reformat(input, output):
    cmd = "ffmpeg -hide_banner -loglevel error -y -i " + input + " -ar 16000 -ac 1 " + output    #sample rate = 16000, 1 audio channel
    subprocess.run(cmd, shell=True)     #Run the command
    return

#Phonemize "phrase" to get phonetic representation
def Phonemize(phrase):
    cmd = "echo " + phrase + " | phonemize" #pipe phrase to phonemizer
    sub = subprocess.Popen(cmd, 
        shell=True, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE, 
        universal_newlines=True)
    key = sub.communicate()[0]
    print(phrase)       #debug
    print('->' + key)   #debug
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
    return

#Return duration of audio file 'filename'
def audio_Duration(filename):
    with contextlib.closing(wave.open(filename,'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)
    return duration
    
#Prepare the dataset to be fed to ASR
def prep_Dataset(uuid, audio, duration, text):
    #HERE UUID
    
    DS = open(tempPath + uuid + '_dataset.json','w')
    sentence = text.replace("'", "").rstrip()
    print('1: ' + sentence)
    stripped = sentence.translate(str.maketrans('', '', '.,!?!;\'-—')) #Strip unnecessary characters
    phonetic = Phonemize(stripped)      #Pass string through Phonemizer
    print('2: ' + phonetic)
    contents = ('{"audio_filename": "' + audio +            #Speech audio-input filename
                '", "duration": ' + str(duration) +         #Duration of the audio input
                ', "text": "' + phonetic.rstrip() + '"}')   #Selected phrase (phonemized)
    DS.write(contents)  #write final prepped dataset, to be read by ASR Module
    DS.close()
    return


#Flask app creation, we can declare folders aside from the defaults
app = Flask(__name__, static_folder="./static/", template_folder="../public_html")
CORS(app)

@app.route('/')
def index():
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
    uuid = request.form['uuid']     # Extract uuid
    phrase = request.form['text']   # Extract phrase string
    
    sampleFile = tempPath + uuid + '_sample.txt'  # Path for sample.txt
    storeTxt = open(sampleFile,'w')     # Create file to hold phrase
    storeTxt.write(phrase)              # Write phrase to file
    storeTxt.close()                    # Close file writing
    os.chmod(sampleFile, 0o755)         # O-RWX, G-RX, U-RX
    return "Phrase -> 'sample.txt'"     # "confirmation" message

@app.route('/Store_Audio', methods=['POST']) #ajax uses GET by def.
def storeAudio():    # write Audio to input.wav, assemble dataset for ASR, create spectrogram
    uuid = request.form['uuid']     # Extract uuid

    sampleAudio = tempPath + uuid + '_sample.wav' # Path for sample.wav
    sampleText = tempPath + uuid + '_sample.txt'  # Path for sample.txt
    inputAudio = tempPath + uuid + '_input.wav'   # Path for input.wav

    audio_data = request.files['audio'].read()  #Extract input audio
    f = open(inputAudio, 'wb')  # create file for input
    f.write(audio_data)         # write audio to file
    f.close()                   # close file

    phrase_file = open(sampleText, "r") # open phrase text file
    phrase = phrase_file.read()         # read phrase text string
    phrase_file.close()                 # close file
    
    audio_Reformat(inputAudio, sampleAudio)             # Reformat audio
    duration = audio_Duration(sampleAudio)              # Get duration of audio
    prep_Dataset(uuid, sampleAudio, duration, phrase)   # Create dataset.json
    os.chmod(sampleAudio, 0o755)                        # O-RWX, G-RX, U-RX
    
    spectroFile = tempPath + uuid + '_spectro.png'    # Path for spectro.png
    Spectro(inputAudio, spectroFile)        # Create the spectrogram image file
    with open(spectroFile, "rb") as png:    # Open the image file & read as bytes
        image_binary = png.read()
        response = make_response(base64.b64encode(image_binary))
        response.headers.set('Content-Type', 'image/gif')
        response.headers.set('Content-Disposition', 'attachment', filename='image.gif')
    return response

@app.route('/Grade', methods=['POST']) #ajax uses GET by def.
def grade():    # Read results file & return strings
    uuid = request.form['uuid']     # Extract uuid
    resultsFile = tempPath + uuid + '_graded.txt' # Path for graded.txt
    
    try:
        with open(resultsFile) as my_file:  # Attempt to open the results file
            graded = my_file.readlines()    # Read lines into an array
        recognized = graded[0]   # 1st line = Speech-to-Text string
        referenced = graded[1]   # 1nd line = Text key (phonetic)
        score = graded[2]        # 3rd line = percentage grade
        return (recognized + '\n' + referenced + '\n' + score)
    except:
        return('###')   # "Error Code" for no file or it's not the proper 2 lines

@app.route('/Clear', methods=['POST']) #ajax uses GET by def.
def Clear():    # clear /temp/
    uuid = request.form['uuid']     # Extract uuid
    clear_Directory(tempPath, uuid) # Call method to empty temp files
    return("cleared.")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)    #localhost
