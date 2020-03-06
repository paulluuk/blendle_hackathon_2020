import glob
import os
import random

import animate


class Fighter:
    def __init__(self, path):
        config = self.getConfig(path)

        self.animations = self.createAnimations(path)
        self.backgrounds = self.loadBackgrounds(path)

        self.block_time = 4
        self.blocking = 0
        self.brain_cmd = config["cmd"]
        self.brain_path = config["path"]
        self.disabled = False
        self.enemy = None
        self.health = 100
        self.hitDistance = 100  # how far your hits reach
        self.jump_speed = 30
        self.jump_speed_now = 0
        self.key = 0
        self.maxX = 0
        self.minX = 0
        self.name = config["name"]
        self.path = path
        self.position = "stand"
        self.punch_damage = 10
        self.state = "IDLE"
        self.timeout = 0
        self.timeout_time_block = 8  # how long we have to wait after blocking
        self.timeout_time_default = 5  # how long we have to wait after movement
        self.timeout_time_get_hit = 9  # how long we have to wait after getting hit
        self.timeout_time_punch = 10  # how long we have to wait after punching
        self.walk_speed = 30  # how quickly we move
        self.x = 0
        self.y = 0
        self.y_offset = 0

    def getConfig(self, path):
        brain_config = os.path.join(path, "code", "config.txt")
        data = {}
        with open(brain_config, "r") as config:
            lines = config.readlines()
            for line in lines:
                if line.startswith("#"):
                    pass
                else:
                    key, value = line.strip().split("=")
                    data[key] = value

        brain_file = data["file"]
        fighter_name = data["name"]

        if not brain_file:
            raise (
                Exception(
                    "Could not determine a brain file location inside {}".format(
                        brain_config
                    )
                )
            )
        else:
            brain_file = os.path.join(path, "code", brain_file)
        if not fighter_name:
            raise (
                Exception("Did not specify a bot name inside {}".format(brain_config))
            )

        extension = brain_file.split(".")[-1]
        if extension == "py":
            brain_cmd = "python"
        elif extension == "rb":
            brain_cmd = "ruby"
        else:
            raise (
                Exception(
                    "Could not determine the brain file format from {}".format(
                        brain_file
                    )
                )
            )

        return {"cmd": brain_cmd, "path": brain_file, "name": fighter_name}

    def get_info_line(self):
        return "{} {} {} {} {} {}".format(
            self.x,
            self.y_offset,
            self.position,
            self.state,
            self.health,
            self.is_ready(),
        )

    def is_ready(self):
        return self.timeout <= 0 and self.blocking <= 0 and self.disabled == False

    def update(self, action):

        self.update_gravity()

        if self.enemy.disabled:
            self.switchAnim("VICTORY")
        elif self.is_ready():
            if action in self.get_options():
                if action == "stand":
                    self.stand()
                    self.timeout = self.timeout_time_default
                elif action == "jump":
                    self.jump()
                    self.timeout = self.timeout_time_default
                elif action == "crouch":
                    self.crouch()
                    self.timeout = self.timeout_time_default
                elif action == "block":
                    self.block()
                    self.timeout = self.timeout_time_block
                elif action == "punch":
                    self.punch()
                    self.timeout = self.timeout_time_punch
                elif action == "walk_left":
                    self.walk_left()
                    self.timeout = self.timeout_time_default
                elif action == "walk_right":
                    self.walk_right()
                    self.timeout = self.timeout_time_default
            elif action == None:
                pass
            else:
                raise (
                    Exception(
                        "Action '{}' is currently not a valid action. Valid actions are={}".format(
                            action, self.get_options()
                        )
                    )
                )
        else:
            self.timeout -= 1
            self.blocking -= 1

    def get_options(self):
        if self.position == "stand":
            return [
                "jump",
                "crouch",
                "block",
                "punch",
                "stand",
                "walk_left",
                "walk_right",
            ]
        elif self.position == "jump":
            return ["block", "punch"]
        elif self.position == "crouch":
            return ["stand", "block", "punch", "crouch"]

    def update_gravity(self):
        if self.jump_speed_now != 0:
            self.y_offset += self.jump_speed_now
            self.jump_speed_now -= 3
        if self.y_offset < 0:
            self.jump_speed_now = 0
            self.y_offset = 0
            self.position = "stand"
            self.switchAnim("IDLE")

    def walk_right(self):
        if self.position == "stand":
            self.switchAnim("WALK")
            self.x += self.walk_speed
            self.x = min(self.x, self.maxX)

    def walk_left(self):
        if self.position == "stand":
            self.switchAnim("WALK")
            self.x -= self.walk_speed
            self.x = max(self.x, self.minX)

    def block(self):
        if self.position == "stand":
            self.blocking = self.block_time
            self.switchAnim("BLOCK")
        elif self.position == "crouch":
            self.blocking = self.block_time
            self.switchAnim("CROUCH_BLOCK")

    def punch(self):
        if self.position == "stand":
            self.switchAnim("PUNCH")
        elif self.position == "crouch":
            self.switchAnim("CROUCH_PUNCH")
        elif self.position == "jump":
            self.switchAnim("JUMP_PUNCH")
        if self.canHit():
            self.enemy.get_hit(self.punch_damage)

    def canHit(self):
        crouch_hit_standing = (
            self.position == "crouch" and self.enemy.position == "standing"
        )
        standing_hit_jump = (
            self.position == "standing" and self.enemy.position == "jump"
        )
        if abs(self.getDist()) <= self.hitDistance:
            return (
                crouch_hit_standing
                or standing_hit_jump
                or self.position == self.enemy.position
            )

    def getDist(self):
        return self.enemy.getPos()[0] - self.getPos()[0]

    def jump(self):
        if self.y_offset == 0 and self.position == "stand":
            self.jump_speed_now = self.jump_speed
            self.switchAnim("JUMP")
            self.position = "jump"

    def crouch(self):
        if self.y_offset == 0 and self.position == "stand":
            self.switchAnim("CROUCH")
            self.position = "crouch"

    def stand(self):
        if self.y_offset == 0 and self.position == "crouch":
            self.switchAnim("IDLE")
            self.position = "stand"

    def get_hit(self, damage):
        if self.blocking > 0:
            pass
        else:
            self.timeout = self.timeout_time_get_hit
            self.health -= damage
            if self.health > 0:
                if self.position == "crouch":
                    self.switchAnim("CROUCH_HIT")
                elif self.position == "stand":
                    self.switchAnim("HIT")
                elif self.position == "jump":
                    self.switchAnim("JUMP_HIT")
            else:
                self.switchAnim("KNOCKDOWN")
                self.disabled = True

    def switchAnim(self, anim):
        if self.state != anim:
            self.key = 0
            self.state = anim

    def setEnemy(self, other):
        self.enemy = other

    def getEnemy(self):
        return self.enemy

    def isFlipped(self):
        return self.getPos()[0] > self.enemy.getPos()[0]

    def addAnimation(self, name, images):
        self.animations[name.upper()] = images

    def getImage(self):
        series = self.animations.get(self.state)
        img = series[self.key]
        self.key += 1
        if self.key >= len(series):
            if self.state == "KNOCKDOWN" or self.state == "VICTORY":
                self.key = len(series) - 1
            elif "BLOCK" in self.state and self.blocking > 0:
                self.key = len(series) - 1
            elif "PUNCH" in self.state or "HIT" in self.state or "BLOCK" in self.state:
                if "CROUCH" in self.state:
                    self.switchAnim("CROUCH")
                if "JUMP" in self.state:
                    self.switchAnim("JUMP")
                else:
                    self.switchAnim("IDLE")
            else:
                self.key = 0
        return img

    def setState(self, state):
        self.state = state
        self.key = 0

    def createAnimations(self, basepath):
        folders = os.path.join(basepath, "animations", "*")
        paths = glob.glob(folders)
        d = {}
        for path in paths:
            animation = os.path.split(path)[-1]
            images = animate.get_animation_images(path)
            d[animation.upper()] = images
        return d

    def loadBackgrounds(self, basepath):
        images = glob.glob(os.path.join(basepath, "backgrounds", "*.png"))
        bgs = []
        bgs += [animate.load_image(path) for path in images]
        return bgs

    def getBackground(self):
        return random.choice(self.backgrounds)

    def setPos(self, x, y):
        self.x = x
        self.y = y

    def getPos(self):
        return self.x, self.y - self.y_offset

    def setMaxPos(self, minX, maxX):
        self.minX = minX
        self.maxX = maxX
