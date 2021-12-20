import xml.etree.ElementTree as ET     #XML tree toolkit

xmlpath = "C:/Users/Reccho/Documents/Launch/ISP/libraries/phrases.xml"

#Return total number of phrases in xml file
def phrase_Num():
    tree = ET.parse(xmlpath)   # Create tree from xml file
    root = tree.getroot()
    return len(root.findall('.//phrase'))
