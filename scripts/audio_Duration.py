def audio_Duration(filename):
  with contextlib.closing(wave.open(filename,'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)
        #print(duration)
    return duration

filename = "sample.wav"
D = audio_Duration(filename)
print(D)
