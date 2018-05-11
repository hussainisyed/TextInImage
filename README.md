# TextInImage

This program practices steganography by hiding and revealing text inside of images.

# Written By

Syed Hussaini

# Application Architecture

This program takes as input a path to a jpeg image and a string of characters. The program then loops through all of the pixels in the image and embeds the text in the least significant bit of each RGB value within each pixel. Pixels where no data is to be embedded are simply copied over from the original image.

# Execution Instructions

usage: ./TextInImage [path to image] [-e string] [-d] [-h]

positional arguments:
  path 		The relative path of the image to use

optional arguments:
  -h, --help		show this help message and exit
  -e TEXT, --encode TEXT    Text to encode in the image
  -d, --decode		Decode from an image
