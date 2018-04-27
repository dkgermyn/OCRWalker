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

def get_text_from_XML(xmlfile):
    tree = ET.parse(xmlfile)
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
    return strings

# convert image to greyscale and save

def preprocess_image(imagefile):
    image = cv2.imread(imagefile)

    grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    base = os.path.splitext(imagefile)[0]
    # print(base) # debug
    print(os.path.dirname(imagefile))
    filename = "processed\{}_processed.png".format(base)
    print(filename)

    cv2.imwrite(filename, grayscale)

    # resize image
    im = Image.open(filename)
    basewidth = 7016
    wpercent = (basewidth / float(im.size[0]))
    hsize = int((float(im.size[1]) * float(wpercent)))
    im = im.resize((basewidth, hsize), Image.ANTIALIAS)
    im.save(filename, dpi=(600,600))

    return filename

# perform OCR on the processed image

def ocr_image(imagefile, language):
    text = pytesseract.image_to_string(Image.open(imagefile), lang=language)

    # clean up ligatures and remove line breaks
    text = unicodedata.normalize("NFKD", text)
    text = text.replace("\n", " ").replace("\r", "")

    # split remaining strings into a list and remove empty strings
    ocr_output = text.split("  ")
    ocr_output = list(filter(None, ocr_output))

    print("OCR output:")
    print(ocr_output)

    return ocr_output

# compare OCR output to list of strings from XML

def compare_ocr_to_xml(ocr, xml, threshold):
    for a, b in itertools.product(ocr, xml):
        sequence = SequenceMatcher(None, a, b)
        d = sequence.ratio()*100
        if d > threshold:
            print("XML string closely matches OCR output (a {percent}% match) :"
                  "\n XML : {xml}"
                  "\n OCR : {ocr}".format(xml=a, ocr=b, percent=d))
        # TODO store all values in a list or dict?
    # TODO return something?

# teardown
# os.remove(filename)

if __name__ == "__main__":

    if not os.path.exists("processed"):
        os.makedirs("processed")
    if not os.path.exists("processed\\french_test_files"):
        os.makedirs("processed\\french_test_files")

    xml_files_to_match = {}
    ocr_files_to_match = {}

    for file in os.listdir("french_test_files"):
        if file.endswith(".xml"):
            filepath = os.path.join("french_test_files", file)
            xml_strings = get_text_from_XML(filepath)
            prefix = os.path.splitext(file)[0]
            xml_files_to_match[prefix] = xml_strings
        elif file.endswith(".jpg"):
            filepath = os.path.join("french_test_files", file)
            process = preprocess_image(filepath)
            ocr_strings = ocr_image(process, "fra")
            prefix = os.path.splitext(file)[0]
            ocr_files_to_match[prefix] = ocr_strings

    for key, value in xml_files_to_match.items():
        if key in ocr_files_to_match:
            # TODO : checking this in to go back to work on ION (4/27/2018)
            # compare XML text to OCR text, spit all out into report