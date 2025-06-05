import zlib, base64
import file_mngr.conf_mngr as conf
from PIL import Image


def decode(string) -> str:
    """
    decodes a supported binary string (for now - only the first LSB layer of RGBA), by turning it into a decimal int, afterwards making it into bytes,
    which then decodes the bytes as base64. finally, that is decompressed with zlib, which return the encoded file's content
    :param string: string of 0 and 1
    :return: decoded text
    """
    conf.logmn.log_info("attempting to decode...  (i might sometimes appear after the 'decoding successful' message, pls ignore it if there's no error of course)")
    try:
        dec_str = int(string, 2)
        byts = dec_str.to_bytes((dec_str.bit_length() + 7) // 8, 'big')
        data = zlib.decompress(base64.b64decode(byts))
        return str(data)[2:-1].replace('\\n', '\n')
    except Exception as e:
        conf.logmn.log_error(f'error! {e}')


def read_png_RGBA(file, include_file=False) -> list[list]:  # big part of the code by myersjustinc on https://stackoverflow.com/questions/31572425/list-all-rgba-values-of-an-image-with-pil
    """
    return png's RGBA decimal values in for of a list, where the elements are RGBA values for a specific pixel
    :param file: png to read from
    :param include_file: return file's data? only used for encoding (as of now), so the default is False
    :return: list, where the elements are RGBA values for a specific pixel
    """
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


def decode_from_png(png, save_to_file=False, file_path=None, hard_write=False):
    """
    decodes supported stuff from (currently) the first layer of LSB in the png (side note to maybe fix - rn supports only decoding english symbols, should add support for non-english?)\n
    if needed (not really in my case but why not ¯\_(ツ)_/¯), can save the decoded stuff to file
    :param png: path to png file which should have encoded stuff in first layers of LSB
    :param save_to_file: should the contents be saved somewhere? if so, pick True. default False
    :param file_path: path (with file) to where the contents should be saved. default None, does something only when save_to_file is True
    :param hard_write: should the contents overwrite existing stuff in the file from file_path? if so, pick True. default False (so, if the file isn't empty, it won't save the decoded content there)
    :return: if save_to_file is False, returns decoded text
    """
    conf.logmn.log_info(f'attempting to decode lsb from png {png}')
    rgba = read_png_RGBA(png)
    fin_bin = ''
    for pixel in rgba:
        for value in pixel:
            value = bin(value)[-1]  # when planning to do multi-layer
            fin_bin += value
    if not save_to_file:
        return decode(fin_bin)
    else:
        conf.logmn.log_info(f'decoding successful, attempting to save to {file_path} with overwriting set to {hard_write}')
        if not conf.check_path(file_path):
            with open(file_path, "w") as out:
                out.write(decode(fin_bin))
        elif conf.check_path(file_path) and hard_write:
            with open(file_path, "w") as out:
                out.write(decode(fin_bin))
        else:
            conf.logmn.log_warning(f'file {file_path} is not empty! set hard_write to True if you really wish to overwrite its contents')
