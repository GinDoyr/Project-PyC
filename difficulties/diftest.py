import random


def read_and_return_enemies(difficulty, boss=False):
    """
    reads a difficulty png, chooses a random line of enemies from it, return a dictionary with the count of each enemy to be spawned
    :param difficulty: 'easy', 'medium', 'doom' or 'custom'
    :param boss: should a boss spawn now? default False
    :return: dictionary, where the keys are enemy types and items are their count
    """
    #  prototype, redo of course lol, make it read the png and return the text content from which to read
    spawn_dict = {}
    with open('difeasy.txt', 'r') as i:
        red = i.read()
        lines = red.splitlines()
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
