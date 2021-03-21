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
    cmd = "echo " + string + " | phonemize"
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
