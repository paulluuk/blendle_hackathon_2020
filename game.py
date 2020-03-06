import random

from blendle_hackathon_2020 import fighter, animate


class Game:
    def __init__(self, fighter1, fighter2):
        width, height = 1200, 400
        f_width, f_height = 200, 200

        minWidth = int(width * 0.1) - f_width // 2
        maxWidth = int(width * 0.9) - f_width // 2
        minHeight = int(height * 0.9)

        self.fighter1 = fighter1
        self.fighter1.setPos(minWidth, minHeight)
        self.fighter1.setMaxPos(minWidth, maxWidth)
        self.fighter2 = fighter2
        self.fighter2.setPos(maxWidth, minHeight)
        self.fighter2.setMaxPos(minWidth, maxWidth)

        self.fighter1.setEnemy(self.fighter2)
        self.fighter2.setEnemy(self.fighter1)

        self.background = random.choice(
            [self.fighter1.getBackground(), self.fighter2.getBackground()]
        ).resize((width, height))

        self.images = []

    def update(self):
        self.fighter1.update()
        self.fighter2.update()
        image = self.background.copy()
        for f in [self.fighter1, self.fighter2]:
            img = f.getImage()
            if f.isFlipped(): img = animate.flip(img)
            image = animate.place_on_background(image, img, f.x, f.y - img.size[1] - f.y_offset)
        self.images += [image]


f1 = fighter.Fighter("example_fighter")
f2 = fighter.Fighter("example_fighter")
game = Game(f1, f2)

for i in range(1000):
    game.update()
animate.animate_sequence(game.images, "battle.gif")
