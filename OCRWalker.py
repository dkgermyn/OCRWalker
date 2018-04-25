import os
import cv2
import unicodedata
import pytesseract
import argparse
import itertools
from xml.etree import ElementTree as ET
from difflib import SequenceMatcher
from PIL import Image

# arguments for python command line
# ap = argparse.ArgumentParser()
# ap.add_argument("-i", "--image", required=True, help="input image")
# ap.add_argument("-x", "--xml", required=False, help="corresponding XML file")
# ap.add_argument("-l", "--language", required=True, help="language of input image")
# args = vars(ap.parse_args())

# get text from XML file

tree = ET.parse("test2.xml")
root = tree.getroot()

strings = []
for element in root:
    for branch in element:
        for twig in branch:
            if twig.text:
                processed = unicodedata.normalize("NFKD", twig.text)
                strings.append(processed)

print("XML file contains:")
print(strings)

# # convert image to greyscale and save
#
# # TODO : args
# # image = cv2.imread(args["image"])
# image = cv2.imread("test2.jpg") # TODO remove this
#
# grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# filename = "{}.png".format(os.getpid())
# cv2.imwrite(filename, grayscale)
#
# # resize image
# im = Image.open(filename)
# basewidth = 7016
# wpercent = (basewidth / float(im.size[0]))
# hsize = int((float(im.size[1]) * float(wpercent)))
# im = im.resize((basewidth, hsize), Image.ANTIALIAS)
# im.save(filename, dpi=(600,600))

# perform OCR on the processed image

# TODO args
# text = pytesseract.image_to_string(Image.open(filename), lang=args["language"])
text = pytesseract.image_to_string(Image.open("11820.png"), lang="fra") # TODO remove this

# clean up ligatures and remove line breaks
text = unicodedata.normalize("NFKD", text)
text = text.replace("\n", " ").replace("\r", "")

# split remaining strings into a list and remove empty strings
ocr_output = text.split("  ")
ocr_output = list(filter(None, ocr_output))

print("OCR output:")
print(ocr_output)

# compare OCR output to list of strings from XML

for a, b in itertools.product(strings, ocr_output):
    sequence = SequenceMatcher(None, a, b)
    d = sequence.ratio()*100
    if d > 90:
        print("XML string closely matches OCR output (a {percent}% match) :"
              "\n XML : {xml}"
              "\n OCR : {ocr}".format(xml=a, ocr=b, percent=d))

# for string in strings:
#     print("Looking for string : {string}".format(string=string))
#
#     sequence = SequenceMatcher(None, string, ocr_output)
#
#     if string in text:
#         print("Found string in OCR output")
#     else:
#         print("String not found in OCR output")

# teardown
# os.remove(filename)
