import random

import fighter, animate, comms


class Game:
    def __init__(self, fighter1, fighter2):

        # setup basic width/height
        width, height = 1200, 400
        f_width, f_height = 200, 200

        # define the boundaries of the map
        minWidth = int(width * 0.1) - f_width // 2
        maxWidth = int(width * 0.9) - f_width // 2
        minHeight = int(height * 0.9)

        # create the fighters and put them in the scene
        self.fighter1 = fighter1
        self.fighter1.setPos(minWidth, minHeight)
        self.fighter1.setMaxPos(minWidth, maxWidth)
        self.fighter2 = fighter2
        self.fighter2.setPos(maxWidth, minHeight)
        self.fighter2.setMaxPos(minWidth, maxWidth)

        # make sure the fighters know who they both are
        self.fighter1.setEnemy(self.fighter2)
        self.fighter2.setEnemy(self.fighter1)

        # use a background from either fighter as the backdrop
        self.background = random.choice(
            [self.fighter1.getBackground(), self.fighter2.getBackground()]
        ).resize((width, height))

        # prepare the images that are turned into a gif in the end
        self.images = []

        # setup communications with both fighters (subprocesses)
        self.fighter1comms = comms.InteractiveSession(self.fighter1.brainCMD,
                                                      self.fighter1.brainPATH)
        self.fighter2comms = comms.InteractiveSession(self.fighter2.brainCMD,
                                                      self.fighter2.brainPATH)

    def update(self):

        # get the current information about the fighters
        status1 = self.fighter1.get_info_line()
        status2 = self.fighter2.get_info_line()

        # send the information to fighter1
        self.fighter1comms.write(status1)  # own info first
        self.fighter1comms.write(status2)  # enemy fighter second

        # send the information to fighter2
        self.fighter2comms.write(status2)  # own info first
        self.fighter2comms.write(status1)  # enemy fighter second

        # ask both fighters what they want to do
        action1 = self.fighter1comms.read()
        action2 = self.fighter2comms.read()

        # execute the actions to update the game
        self.fighter1.update(action1)
        self.fighter2.update(action2)

        # create image of current scene
        image = self.background.copy()
        for f in [self.fighter1, self.fighter2]:
            img = f.getImage()
            if f.isFlipped():
                img = animate.flip(img)
            image = animate.place_on_background(
                image, img, f.x, f.y - img.size[1] - f.y_offset
            )
        self.images += [image]
        if (
                self.fighter1.health <= 0
                or self.fighter2.health <= 0
                or len(self.images) > 2000
        ):
            return False
        else:
            return True

    def process(self):

        # while the fight lasts
        while self.update():
            pass
        # add a few more shots for the ending
        for i in range(25):
            self.update()

        self.fighter1comms.terminate()
        self.fighter2comms.terminate()

        animate.animate_sequence(game.images, "battle.gif")


f1 = fighter.Fighter("example_fighter")
f2 = fighter.Fighter("example_fighter")
game = Game(f1, f2)
game.process()
