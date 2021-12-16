import os, sys, subprocess

# you can use librosa.get_duration()

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

text = sys.argv[1]
sox = sox_i(text)
print(sox)
