import os, os.path, subprocess, time

def craft(filename, duration, text):
	contents = "{\"audio_filename\": \"" + filename + "\", \"duration\": " + duration + ", \"text\": \"" + text + "\"}"
	cmd = "echo " + contents + " >dataset.json"
	subprocess.Popen(cmd, 
        shell=True, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE, 
        universal_newlines=True)
	#key = sub.communicate()[0]
	return

# Audio file in cluster: /lnet/aic/personal/nichols/audio/audio/audio.wav
craft("/lnet/aic/personal/nichols/audio/audio.wav", "4.995000", "Well, this is the text.")
