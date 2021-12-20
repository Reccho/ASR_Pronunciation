import xml.etree.ElementTree as ET     #XML tree toolkit

xmlpath = "C:/Users/Reccho/Documents/Launch/ISP/libraries/phrases.xml" #sample

#Search xml file for phrase by id and return text string
def phrase_Get(itemNum):
    #print("getting phrase: " + itemNum) #TEST
    tree = ET.parse(xmlpath)   # Create tree from xml file
    root = tree.getroot()                                                           # Start at root
    text = root.find('.//phrase[@id="{value}"]'.format(value=itemNum)).text         # Search for matching id, pull text
    return text
