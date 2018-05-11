"""
CPSC 353 Project - Text In Image
Written by: Syed Hussaini
CWID: 889757084

This program practices steganography by hiding and revealing text inside of images.
"""

from PIL import Image
import argparse
import math

# Number of pixels to hide the text length
num_text_len_pixels = 11

# The mask to extract the least significant bit of an 8-bit binary number
mask = 0b1


def encode(file_path, text):
    # Check if .jpg image and user entered text
    if not file_path.endswith(".jpeg") and not file_path.endswith(".jpg"):
        raise ValueError("Error: Must be .jpg image")
    if not text.strip():
        raise ValueError("Error: Must input text to encode.")

    # Image from user
    before = Image.open(file_path)
    pixmap_before = before.load()

    text_bits = convert(text)
    num_pixels = before.size[0] * before.size[1]

    # Check if text will fit in image
    if len(text_bits) > (num_pixels - 11) * 3:
        raise ValueError('Error: Input text cannot fit in image.')

    # Image after encode
    after = Image.new(before.mode, before.size)
    pixmap_after = after.load()

    # Embed the input text in the image.
    return encode_text(before, pixmap_before, after, pixmap_after, text_bits)


def encode_text(before, pixmap_before, after, pixmap_after, text_bits):
    num_loops = bin(int(math.ceil(len(text_bits) / 3 + 1)))
    num_loops = num_loops[2:]

    # Encode text length into the image on the first 11 bottom right pixels.
    i = len(num_loops) - 1
    for x in range(num_text_len_pixels):
        r_bin, g_bin, b_bin = get_pixels_bin(pixmap_before, before.size[0] - x - 1, before.size[1] - 1)

        if i >= 0:
            b_bin = set_bit(b_bin, 0) if num_loops[i] == '1' else clear_bit(b_bin, 0)
            i -= 1
        else:
            b_bin = clear_bit(b_bin, 0)
        if i >= 0:
            g_bin = set_bit(g_bin, 0) if num_loops[i] == '1' else clear_bit(g_bin, 0)
            i -= 1
        else:
            g_bin = clear_bit(g_bin, 0)
        if i >= 0:
            r_bin = set_bit(r_bin, 0) if num_loops[i] == '1' else clear_bit(r_bin, 0)
            i -= 1
        else:
            r_bin = clear_bit(r_bin, 0)

        pixmap_after[before.size[0] - x - 1, before.size[1] - 1] = (r_bin, g_bin, b_bin)

    # Encode input text into the image.
    i = 0
    for y in range(before.size[1]):
        for x in range(before.size[0]):

            # Avoid writing over 11 pixels on the bottom right that contain text length
            if y == before.size[1] - 1 and x == before.size[0] - num_text_len_pixels:
                break

            r_bin, g_bin, b_bin = get_pixels_bin(pixmap_before, x, y)
            if i < len(text_bits):
                r_bin = set_bit(r_bin, 0) if text_bits[i] == 1 else clear_bit(r_bin, 0)
                i += 1
            if i < len(text_bits):
                g_bin = set_bit(g_bin, 0) if text_bits[i] == 1 else clear_bit(g_bin, 0)
                i += 1
            if i < len(text_bits):
                b_bin = set_bit(b_bin, 0) if text_bits[i] == 1 else clear_bit(b_bin, 0)
                i += 1

            pixmap_after[x, y] = (r_bin, g_bin, b_bin)

    return after


def decode(file_path):
    img = Image.open(file_path)
    pixmap = img.load()

    # Extract text length
    bits = ''
    for x in range(num_text_len_pixels):
        r_bin, g_bin, b_bin = get_pixels_bin(pixmap, img.size[0] - x - 1, img.size[1] - 1)
        bits = str(b_bin & mask) + bits
        bits = str(g_bin & mask) + bits
        bits = str(r_bin & mask) + bits

    # Number of pixels to read from
    loop_count = int(bits, 2)

    # Read text from image
    result = []
    index = 0
    for y in range(img.size[1]):
        for x in range(img.size[0]):

            if index == loop_count:
                break

            r_bin, g_bin, b_bin = get_pixels_bin(pixmap, x, y)
            result.append(r_bin & mask)
            result.append(g_bin & mask)
            result.append(b_bin & mask)

            index += 1

    return revert(result)

"""
This function returns 3 RGB values from pixel map at given x and y coordinates.
Returns value as binary numbers
"""
def get_pixels_bin(pixmap, x, y):
    r, g, b = pixmap[x, y]
    r_bin = int(bin(r), 2)
    g_bin = int(bin(g), 2)
    b_bin = int(bin(b), 2)
    return r_bin, g_bin, b_bin


# This function sets a single bit in value parameter to 1
def set_bit(value, bit):
    return value | (1 << bit)


# This function sets a single bit in value parameter to 0
def clear_bit(value, bit):
    return value & ~(1 << bit)


# This function converts string to list of bits
def convert(str):
    result = []
    for c in str:
        bits = bin(ord(c))[2:]
        bits = '00000000'[len(bits):] + bits
        result.extend([int(b) for b in bits])
    return result


# This function reverts bits back to string
def revert(bits):
    chars = []
    for b in range(int(len(bits) / 8)):
        byte = bits[b * 8:(b + 1) * 8]
        chars.append(chr(int(''.join([str(bit) for bit in byte]), 2)))
    return ''.join(chars)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(usage='./TextInImage [path] [-e string] [-d] [-h]')
    parser.add_argument('path', help='The relative path of the image to use')
    parser.add_argument('-e', '--encode', help='Encode text in image')
    parser.add_argument('-d', '--decode', help='Decode text from image', action='store_true')
    args = parser.parse_args()

    if args.encode:
        encode(args.path, args.encode).save('hidden.png')
    elif args.decode:
        print(decode(args.path))
