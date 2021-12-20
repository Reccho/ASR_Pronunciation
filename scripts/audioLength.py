import sys, librosa

def duration(filepath):
    length = librosa.get_duration(filename=filepath)
    return length


t = duration('../temp/' + sys.argv[1])
print(t)
