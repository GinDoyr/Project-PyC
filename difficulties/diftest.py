import numpy as np
from io import BytesIO
from png_lsb_stuff.lsb_decoder import decode_from_png
from png_lsb_stuff.lsb_encoder import encode_file_to_png

# lets do like that: easy <= 20 diff points, medium <= 40 diff point, doom <= 80 diff points
# 0 - 1 diff point; 1 - 3 points; 2 - 4 points
# boss logic in game_loop.py, just increase stats with difficulty

easy = [[5, 3, 0],
        [10, 2, 0],
        [8, 4, 0]]  # whatever just do like that for now

medium = [[10, 6, 0],
          [15, 7, 0],
          [30, 0, 0]]

doom = [[80, 0, 0],
        [30, 10, 0],
        [5, 20, 0]]  # balancing? naaah lol, if you die - skill issue

custom = [[200, 0, 0],
          [0, 40, 0]]  # lulz

diffs = [easy, medium, doom, custom]
dd = {0: 'easy', 1: 'medium', 2:'doom', 3:'custom'}


def get_default(diff_num):
    return diffs[diff_num]


def encode_difficulties(editor_list=None):
    if editor_list:
        diff = editor_list[1:]
        text = dd.get(editor_list[0])
        difbit = BytesIO()
        for row in diff:
            row = [str(i) for i in row]
            difbit.write(','.join(row).encode('utf-8') + b'\n')
        difbit.seek(0)  # dunno if this is required but just to be safe
        encode_file_to_png(difbit, f'difficulties/orig_pngs/{text}.png', f'difficulties/{text}.png', True)
    else:
        for i in range(len(diffs)): # this one's meant to be run right here, no path changing
            diff = diffs[i]
            text = dd.get(i)
            difbit = BytesIO()
            for row in diff:
                row = [str(i) for i in row]
                difbit.write(','.join(row).encode('utf-8') + b'\n')
            difbit.seek(0)
            encode_file_to_png(difbit, f'orig_pngs/{text}.png', f'{text}.png', True)


def read_and_return_enemies(difficulty, editor=False):
    """
    reads a difficulty png, chooses a random line of enemies from it, return a dictionary with the count of each enemy to be spawned
    :param difficulty: 'easy', 'medium', 'doom' or 'custom'
    :param editor: for difficulty editor, ignore
    :return: dictionary, where the keys are enemy types and items are their count
    """
    # v3! and i think this is the best one yet! :D
    spawn_dict = {}
    read = decode_from_png(
        f'difficulties/{difficulty}.png')  # written like that because i use this path in game_loop.py
    lines = read.splitlines()
    if not editor:
        line = lines[np.random.choice(len(lines))]
        nums = [int(i) for i in line.split(',')]
        for n in range(len(nums)):
            spawn_dict[n] = nums[n]
        return spawn_dict
    else:
        ret_list = []
        for line in lines:
            nums = [int(i) for i in line.split(',')]
            ret_list.append(nums)
        return ret_list
