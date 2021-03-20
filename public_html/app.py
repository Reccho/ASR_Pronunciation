from flask import Flask, request    #Flask for post requests
from flask_cors import CORS         #bypassing CORS locally
import xml.etree.ElementTree as ET     #XML tree toolkit
import os, os.path, subprocess, time     


# create the Flask app
app = Flask(__name__)
CORS(app)

@app.route('/Action', methods=['POST']) #ajax uses GET by def.
def query():
    if request.form['action'] == "grade": # get audio --> return grade
        return 1
    elif request.form['action'] == "numPhrase": # get phrase number --> return string
        return 2
    elif request.form['action'] == "getPhrase": # get phrase number --> return string
        return 3
    elif request.form['action'] == "getDataset": # get dataset name --> return dataset title, open xml tree
        pass
    return ":)"

if __name__ == '__main__':
    # run app in debug mode on port 5000
    app.run(debug=True, port=5000)
