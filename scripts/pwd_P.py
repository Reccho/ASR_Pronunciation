import os, sys, subprocess

# NO
# use os.path.abspath()

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

text = sys.argv[1]
pwd = pwd_P(text)
print(pwd)
