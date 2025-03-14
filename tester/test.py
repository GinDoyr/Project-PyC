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
    text = open(file_path).read() + '$END-ZAE'
    code = base64.b64encode(zlib.compress(text.encode('utf-8'), 9))
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


def read_png_RGBA(file, include_file=False):  # big part of the code by myersjustinc on https://stackoverflow.com/questions/31572425/list-all-rgba-values-of-an-image-with-pil
    imgobj = Image.open(file)
    pixels = imgobj.convert('RGBA')
    data = pixels.getdata()
    lofpixels = []
    for pixel in data:
        lofpixels.extend(pixel)
    imgobj.close()
    if include_file:
        return lofpixels, pixels
    else:
        return lofpixels


def replace_LSB_in_png(bin_to_replace_with, pngfile):
    rgba, out_png = read_png_RGBA(pngfile, True)
    rgba = [rgba[i:i+4] for i in range(0, len(rgba), 4)]
    lsb_to_replace = []
    for i in range(0, len(bin_to_replace_with), 4):
        lsb_to_replace.append([bin_to_replace_with[i], bin_to_replace_with[i+1], bin_to_replace_with[i+2], bin_to_replace_with[i+3]]) # i know this is too big and could be done more efficiently but not now k, fix sometime later
    if len(lsb_to_replace) > len(rgba):
        print('ABORT REPLACING LSB! not enough bytes to replace the whole file! ')
    out_data = []
    for i in range(len(rgba)):
        if i in range(len(lsb_to_replace)):
            out_byte = []
            for bit in range(4):
                lsb = int(format(rgba[i][bit], 'b'))
                out_byte.append(int(str((lsb & ~1) | int(lsb_to_replace[i][bit])), 2)) # honestly this is some magic to me lol, but hey it works
            print(out_byte)
            out_data.append(tuple(out_byte))
        else:
            out_data.append(tuple(rgba[i]))
    out_png.putdata(out_data)
    Image.open(out_png.save(pngfile))


test = zip_and_encode('settings.ini')
test_bytes = read_png_RGBA('../difficulties/easy.png')
