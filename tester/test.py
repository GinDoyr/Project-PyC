import zlib, base64
from PIL import Image
from io import BytesIO


def zip_and_encode(file_path):
    """
    reads the file's content, zips it with zlib, converts the result to binary and returns the resulting binary in a
    form of string
    :param file_path: what text-like file to encode
    :return: string of 0 and 1 to do stuff with
    """
    text = open(file_path).read() + '$END'
    code = base64.b64encode(zlib.compress(text.encode('utf-8'), 9))
    print(code)
    binar = ' '.join(format(ord(x), 'b') for x in str(code)[2:])
    fin = []
    for i in binar.split(' '):
        while len(i) != 8:
            i = '0' + i
        fin.append(i)
    print('debug note for z_a_e: lsb to change:', len(''.join(fin)))
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


def bin_to_png(bytes, out_path_name):
    Image.open(BytesIO(bytes)).save(out_path_name)


def read_png_RGBA(file):  # by myersjustinc on https://stackoverflow.com/questions/31572425/list-all-rgba-values-of-an-image-with-pil
    imgobj = Image.open(file)
    pixels = imgobj.convert('RGBA')
    data = pixels.getdata()
    lofpixels = []
    for pixel in data:
        lofpixels.extend(pixel)
    imgobj.close()
    return lofpixels


def replace_LSB_in_png(bin_to_replace_with, pngfile):
    rgba = read_png_RGBA(pngfile)
    if len(bin_to_replace_with) > len(rgba):
        print('ABORT REPLACING LSB! not enough bytes to replace the whole file! ')
    for i in range(len(rgba)):
        lsb = int(format(rgba[i], 'b'))
        if i in range(len(bin_to_replace_with)):
            rgba[i] = int(str((lsb & ~1) | int(bin_to_replace_with[i])), 2)
        else:
            rgba[i] = lsb
    for i in range(len(rgba)):
        rgba[i] = str(rgba[i])
    rgba = ''.join(rgba)
    out = int(rgba, 2).to_bytes((len(rgba) + 7) // 8, byteorder='big')
    print(out)
    bin_to_png(out, pngfile[pngfile.rfind('/')+1:])


test = zip_and_encode('settings.ini')
test_bytes = read_png_RGBA('../difficulties/easy.png')
replace_LSB_in_png(test, '../difficulties/easy.png')
