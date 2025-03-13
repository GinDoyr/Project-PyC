import zlib, base64
from PIL import Image

def zip_and_encode(file_path):
    """
    reads the file's content, zips it with zlib, converts the result to binary and returns the resulting binary in a
    form of string
    :param file_path: what text-like file to encode
    :return: string of 0 and 1 to do stuff with
    """
    text = open(file_path).read()
    code = base64.b64encode(zlib.compress(text.encode('utf-8'), 9))
    binar = ' '.join(format(ord(x), 'b') for x in str(code)[2:])
    fin = []
    for i in binar.split(' '):
        while len(i) != 8:
            i = '0' + i
        fin.append(i)
    return ''.join(fin)


def decode(string):
    """
    currently only decodes binary strings, need to make it to read LSBs of pngs
    :param string: string of 0 and 1
    :return: decoded text
    """
    fin = int(''.join(string), 2)
    code = bytes(fin.to_bytes((fin.bit_length() + 7) // 8, 'big').decode(), 'utf-8')
    data = zlib.decompress(base64.b64decode(code))
    return str(data)[2:].replace('\\n', '\n')


def read_png_RGBA(file):  # by myersjustinc on https://stackoverflow.com/questions/31572425/list-all-rgba-values-of-an-image-with-pil
    imgobj = Image.open(file)
    pixels = imgobj.convert('RGBA')
    data = pixels.getdata()
    lofpixels = []
    for pixel in data:
        lofpixels.extend(pixel)
    return lofpixels

def replace_LSB_in_png(bin_to_replace_with, pngfile):
    rgba = read_png_RGBA(pngfile)
    for i in len(bin_to_replace_with):
        lsb = int(format(rgba[i], 'b'))
        result_pixel = (lsb & ~1) | bin_to_replace_with[i]

test = zip_and_encode('settings.ini')
result = decode(test)
test_bytes = read_png_RGBA('Chronosis.png')
twob = format(test_bytes[0], 'b')
print(type(twob))
print(twob, int(twob) & ~1)
