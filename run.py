import glob, os, random

import game, fighter

fighters = glob.glob(os.path.join("fighters", "*"))
f1 = fighter.Fighter(random.choice(fighters))
f2 = fighter.Fighter(random.choice(fighters))
game.Game(f1, f2).process()
