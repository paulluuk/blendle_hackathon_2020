import glob, os, random

import game, fighter

# get a list of available fighters
fighters = glob.glob(os.path.join("fighters", "*"))
# create the left fighter
f1 = fighter.Fighter(random.choice(fighters))
# create the right fighter
f2 = fighter.Fighter(random.choice(fighters))
# launch the game
game.Game(f1, f2).process()
