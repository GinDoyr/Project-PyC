import random
from png_lsb_stuff.lsb_decoder import decode_from_png
# from png_lsb_stuff.lsb_encoder import encode_file_to_png

# might actually use a csv for this, columns are enemy types and rows are their count / wave of them. boss trigger is a column as well
# you shouldn't tell me the txt i did rn for the enemies is bad as hell, i know, it's meant to be like that cause it temporary for god's sake
def read_and_return_enemies(difficulty, boss=False):
    """
    reads a difficulty png, chooses a random line of enemies from it, return a dictionary with the count of each enemy to be spawned
    :param difficulty: 'easy', 'medium', 'doom' or 'custom'
    :param boss: should a boss spawn now? default False
    :return: dictionary, where the keys are enemy types and items are their count
    """
    #  prototype v2, bit better but still has room for improvement
    spawn_dict = {}
    read = decode_from_png(f'difficulties/{difficulty}.png')
    lines = read.splitlines()
    if boss:
        boss_list = []
        for line in lines:
            if line.startswith('BOSS'):
                boss_list.append(line)
        indx = random.randrange(len(boss_list))
        pick = boss_list[indx]
        enemies = pick.split(' ')
        for enemy in enemies:
            temp = enemy.split(':')
            spawn_dict[temp[0]] = int(temp[1])
        return spawn_dict
    else:
        lst = []
        for line in lines:
            if line.startswith('1'):
                lst.append(line)
        indx = random.randrange(len(lst))
        pick = lst[indx]
        enemies = pick.split(' ')
        for enemy in enemies:
            temp = enemy.split(':')
            spawn_dict[temp[0]] = int(temp[1])
        return spawn_dict


# encode_file_to_png('difeasy.txt', 'easy.png', 'difficulties/easy.png')
print(read_and_return_enemies('easy'))
