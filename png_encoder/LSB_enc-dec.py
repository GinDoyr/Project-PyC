import zlib, base64, sys
import file_mngr.conf_mngr as conf
from PIL import Image


def zip_and_encode(file_path):
    """
    reads the file's content, zips it with zlib, converts the result to binary and returns the resulting binary in a
    form of string
    :param file_path: what text-like file to encode
    :return: string of 0 and 1 to do stuff with
    """
    conf.logmn.log_info(f'trying to open file to encode: {file_path}')
    try:
        text = open(file_path, encoding='utf-8').read()
        conf.logmn.log_info(f'attempting to encode...')
        code = base64.b64encode(zlib.compress(text.encode('utf-8'), 9))
        print(code)
        binar = ' '.join(format(ord(x), 'b') for x in str(code)[2:])
        print(binar)
        fin = []
        for i in binar.split(' '):
            while len(i) != 8:
                i = '0' + i
            fin.append(i)
        return ''.join(fin)
    except Exception as e:
        conf.logmn.log_error(f'error! {e}')


def decode(string):
    """
    currently only decodes binary strings, need to make it to read LSBs of pngs
    :param string: string of 0 and 1
    :return: decoded text
    """
    sys.set_int_max_str_digits(999999999)
    conf.logmn.log_info(f'attempting to decode...')
    print(string)
    try:
        dec_str = int(string, 2)
        binar = dec_str.to_bytes((dec_str.bit_length() + 7) // 8, 'big')
        code = bytes(binar.decode(), 'utf-8')
        print(code)
        data = zlib.decompress(base64.b64decode(code))
        return str(data)[2:].replace('\\n', '\n')
    except Exception as e:
        raise e  # TEMP!! REMOVE AFTER FINDING OUT HOW TO DECODE
        conf.logmn.log_error(f'error! {e}')


def read_png_RGBA(file, include_file=False):  # big part of the code by myersjustinc on https://stackoverflow.com/questions/31572425/list-all-rgba-values-of-an-image-with-pil
    conf.logmn.log_info(f'attempting to read png rgba: {file}')
    try:
        imgobj = Image.open(file)
        pixels = imgobj.convert('RGBA')
        data = pixels.getdata()
        lofpixels = []
        for pixel in data:
            lofpixels.extend(pixel)
        lofpixels = [lofpixels[i:i+4] for i in range(0, len(lofpixels), 4)]
        if include_file:
            return lofpixels, pixels
        else:
            return lofpixels
    except Exception as e:
        conf.logmn.log_error(f'error! {e}')


def replace_LSB_in_png(bin_to_replace_with, pngfile, out_path_png):
    """
    replaces lsbs of the png to the input binary string
    :param bin_to_replace_with: binary string to encode in lsbs of the png
    :param pngfile: path to png file
    """
    conf.logmn.log_info(f'attempting to replace LSB for {pngfile}')
    try:
        rgba, out_png = read_png_RGBA(pngfile, True)
        lsb_to_replace = []
        for i in range(0, len(bin_to_replace_with), 4):
            lsb_to_replace.append([bin_to_replace_with[i], bin_to_replace_with[i+1], bin_to_replace_with[i+2], bin_to_replace_with[i+3]]) # i know this is too big and could be done more efficiently but not now k, fix sometime later
        if len(lsb_to_replace) > len(rgba):
            conf.logmn.log_warning(f'ABORT REPLACING LSB! not enough bytes to replace the whole file! input len: {len(lsb_to_replace)}, png len: {len(rgba)}')
            # some testing for multi-lsb encoding
            print(rgba)
            print(lsb_to_replace)
            raise Exception('written above')
        out_data = []
        for i in range(len(rgba)):
            if i in range(len(lsb_to_replace)):
                out_byte = []
                for bit in range(4):
                    lsb = int(format(rgba[i][bit], 'b'))
                    out_byte.append(int(str((lsb & ~1) | int(lsb_to_replace[i][bit])), 2))
                out_data.append(tuple(out_byte))
            else:
                out_data.append(tuple(rgba[i]))
        out_png.putdata(out_data)
        try:
            Image.open(out_png.save(out_path_png))
        except AttributeError:  # this just ignores that unknown error that keeps happening when saving, idk why it does that but yeah
            pass
    except Exception as e:
        conf.logmn.log_error(f'error! {e}')


def encode_file_to_png(file, png, out_png_path):
    inp = zip_and_encode(file)
    replace_LSB_in_png(inp, png, out_png_path)


def decode_from_png(png, save_to_file=False, file_path=False):
    conf.logmn.log_info(f'attempting to decode lsb from png {png}')
    rgba = read_png_RGBA(png)
    fin_bin = ''
    for pixel in rgba:
        for value in pixel:
            value = bin(value)[2:]
            while len(value) != 8:
                print(value)
                value = '0' + value
            fin_bin += value
    return decode(fin_bin)


encode_file_to_png('settings.ini', 'easy.png', 'easy.png')
decode_from_png('easy.png')
