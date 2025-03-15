import zlib, base64
import file_mngr.conf_mngr as conf
from PIL import Image


def zip_and_encode(file_path):
    """
    reads the file's content, zips it with zlib, converts the result to binary and returns the resulting binary in a
    form of string
    :param file_path: what text-like file to encode
    :return: string of 0 and 1 to do stuff with
    """
    # note: some characters are unsupported for encoding (reading???), which ones i currently do not know, so just hope you dont run into them while encoding stuff :P
    conf.logmn.log_info(f'trying to open file to encode: {file_path}')
    try:
        text = open(file_path).read()
        conf.logmn.log_info(f'attempting to encode...')
        code = base64.b64encode(zlib.compress(text.encode('utf-8'), 9))
        binar = ' '.join(format(ord(x), 'b') for x in str(code)[2:])
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
    conf.logmn.log_info(f'attempting to decode...')
    try:
        fin = int(''.join(string), 2)
        bt_to_decode = fin.to_bytes((fin.bit_length() + 7) // 8, 'big')
        binar = ' '.join(format(ord(x), 'b') for x in str(bt_to_decode)[2:str(bt_to_decode).find('\\x')])
        fin = []
        for i in binar.split(' '):
            while len(i) != 8:
                i = '0' + i
            fin.append(i)
        binar = int(''.join(fin), 2)
        binar = binar.to_bytes((binar.bit_length() + 7) // 8, 'big')
        code = bytes(binar.decode(), 'utf-8')
        data = zlib.decompress(base64.b64decode(code))
        return str(data)[2:].replace('\\n', '\n')
    except Exception as e:
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
        if include_file:
            return lofpixels, pixels
        else:
            return lofpixels
    except Exception as e:
        conf.logmn.log_error(f'error! {e}')


def replace_LSB_in_png(bin_to_replace_with, pngfile):
    """
    replaces lsbs of the png to the input binary string
    :param bin_to_replace_with: binary string to encode in lsbs of the png
    :param pngfile: path to png file
    """
    conf.logmn.log_info(f'attempting to replace LSB for {pngfile}')
    try:
        rgba, out_png = read_png_RGBA(pngfile, True)
        rgba = [rgba[i:i+4] for i in range(0, len(rgba), 4)]
        lsb_to_replace = []
        for i in range(0, len(bin_to_replace_with), 4):
            lsb_to_replace.append([bin_to_replace_with[i], bin_to_replace_with[i+1], bin_to_replace_with[i+2], bin_to_replace_with[i+3]]) # i know this is too big and could be done more efficiently but not now k, fix sometime later
        if len(lsb_to_replace) > len(rgba):
            conf.logmn.log_warning(f'ABORT REPLACING LSB! not enough bytes to replace the whole file! input len: {len(lsb_to_replace)}, png len: {len(rgba)}')
            raise Exception
        out_data = []
        for i in range(len(rgba)):
            if i in range(len(lsb_to_replace)):
                out_byte = []
                for bit in range(4):
                    lsb = int(format(rgba[i][bit], 'b'))
                    out_byte.append(int(str((lsb & ~1) | int(lsb_to_replace[i][bit])), 2)) # honestly this is some magic to me lol, but hey it works
                out_data.append(tuple(out_byte))
            else:
                out_data.append(tuple(rgba[i]))
        out_png.putdata(out_data)
        try:
            Image.open(out_png.save(pngfile[pngfile.rfind('/')+1:]))
        except AttributeError:  # this just ignores that unknown error that keeps happening when saving, idk why it does that but yeah
            pass
    except Exception as e:
        conf.logmn.log_error(f'error! {e}')
