from png_lsb_stuff.lsb_decoder import read_png_RGBA, zlib, base64, conf


def zip_and_encode(file_path, byte=False):
    """
    reads the file's content, zips it with zlib, converts the result to binary and returns the resulting binary in a
    form of string
    :param file_path: what text-like file to encode
    :return: string of 0 and 1 to do stuff with
    """
    conf.logmn.log_info(f'trying to open file to encode: {file_path}')
    try:
        if byte:
            text = file_path.getvalue().decode('utf-8')
        else:
            text = open(file_path, encoding='utf-8').read()
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


def replace_LSB_in_png(bin_to_replace_with, pngfile, out_path_png):
    """
    replaces lsbs of the png to the input binary string
    :param bin_to_replace_with: binary string to encode in lsbs of the png
    :param pngfile: path to png file
    :param out_path_png: path to output png file (with file included)
    """
    conf.logmn.log_info(f'attempting to replace LSB for {pngfile}')
    try:
        rgba, out_png = read_png_RGBA(pngfile, True)
        lsb_to_replace = []
        for i in range(0, len(bin_to_replace_with), 4):
            lsb_to_replace.append([bin_to_replace_with[i], bin_to_replace_with[i+1], bin_to_replace_with[i+2], bin_to_replace_with[i+3]]) # i know this is too big and could be done more efficiently but not now k, fix sometime later
        if len(lsb_to_replace) > len(rgba):
            conf.logmn.log_warning(f'ABORT REPLACING LSB! not enough bytes to replace the whole file! input len: {len(lsb_to_replace)}, png len: {len(rgba)}')
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
        conf.logmn.log_info(f'done saving, trying to put to output path: {out_path_png}')
        try:
            out_png.save(out_path_png)
        except AttributeError:  # this just ignores that unknown error that keeps happening when saving, idk why it does that but yeah
            pass
    except Exception as e:
        conf.logmn.log_error(f'error! {e}')


def encode_file_to_png(file, png, out_png_path, bytes=False):
    """
    function name. WARNING: will overwrite existing file at out_png_path (if there is one)!
    :param file: text-like file to encode
    :param png: png file to encode to
    :param out_png_path: resulting png path (WILL OVERWRITE EXISTING!)
    :param bytes: is input byte-like object (io.BytesIO)? def. False
    """
    conf.logmn.log_info(f'attempting to encode {file} into {png}')
    inp = zip_and_encode(file, bytes)
    replace_LSB_in_png(inp, png, out_png_path)
