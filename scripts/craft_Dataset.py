import sys, os.path, librosa, json

def craft_Dataset(arguments):
    filename = os.path.abspath('../temp/' + arguments[1])
    duration = librosa.get_duration(filename='../temp/' + arguments[1])
    text = arguments[2]

    contents = json.dumps({
        "audio_filename": filename,
        "duration": duration,
        "text": text
    })

    with open('dataset.json', 'w') as dataset:
        dataset.write(contents)

    return contents


craft_Dataset(sys.argv)
