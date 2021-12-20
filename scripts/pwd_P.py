import sys, os.path

def absolutePath(filepath):
    absolute = os.path.abspath(filepath)
    return absolute


p = absolutePath('../temp/' + sys.argv[1])
print(p)
