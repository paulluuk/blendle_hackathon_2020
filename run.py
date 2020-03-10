import glob, os, random

import game, fighter

DIR = os.path.dirname(__file__)

# get a list of available fighters
fighters = glob.glob(os.path.join(DIR, "fighters", "*"))

# create a fighting roster
for fighter_path1 in fighters:
    for fighter_path2 in fighters:
        # create the left fighter
        f1 = fighter.Fighter(fighter_path1)
        # create the right fighter
        f2 = fighter.Fighter(fighter_path2)
        # launch the game
        game.Game(f1, f2).process()
