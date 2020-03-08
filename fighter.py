import glob
import os
import random

import animate


class Fighter:
    def __init__(self, path):
        config = self.getConfig(path)

        self.block_time = 4
        self.blocking = 0
        self.brain_cmd = config["cmd"]
        self.brain_path = config["path"]
        self.disabled = False
        self.enemy = None
        self.health = 100
        self.hitDistance = 100  # how far your hits reach
        self.jump_speed = 30
        self.jump_speed_now = 8.6
        self.fall_speed = 9.8
        self.key = 0
        self.maxX = 0
        self.minX = 0
        self.name = config["name"]
        self.path = path
        self.position = "stand"
        self.punch_damage = 10
        self.current_anim = "IDLE"
        self.timeout = 0
        self.timeout_time_block = 2  # how long we have to wait after blocking
        self.timeout_time_default = 1  # how long we have to wait after movement
        self.timeout_time_get_hit = 3  # how long we have to wait after getting hit
        self.timeout_time_punch = 3  # how long we have to wait after punching
        self.walk_speed = 30  # how quickly we move
        self.x = 0
        self.y = 0
        self.y_offset = 0
        self.flipped = False

        self.animations = self.createAnimations(path)
        self.backgrounds = self.loadBackgrounds(path)

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
        return "{x} {y} {facing} {pos} {anim} {health} {ready}".format(
            x=self.x,
            y=self.y_offset,
            facing="left" if self.flipped else "right",
            pos=self.position,
            anim=self.current_anim,
            health=self.health,
            ready=self.is_ready(),
        )

    def is_ready(self):
        return self.timeout <= 0 and self.blocking <= 0 and self.disabled == False

    def update(self, action):

        self.update_gravity()

        if self.disabled:
            self.switchAnim("knockdown")
            return
        elif self.enemy.disabled:
            self.switchAnim("victory")
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
        if self.y_offset >= 0 or self.jump_speed_now != 0:
            self.y_offset += self.jump_speed_now
            self.jump_speed_now -= self.fall_speed
        if self.y_offset < 0:
            self.jump_speed_now = 0
            self.y_offset = 0
            self.position = "stand"
            self.switchAnim("idle")
        self.y_offset = int(self.y_offset)

    def walk_right(self):
        if self.x < self.enemy.x:
            furthestX = self.enemy.x - int(self.hitDistance*0.9)
        else:
            furthestX = self.maxX
        if self.position == "stand":
            self.switchAnim("walk")
            self.x += self.walk_speed
            self.x = min(self.x, furthestX)
            self.flipped = False

    def walk_left(self):
        if self.x > self.enemy.x:
            furthestX = self.enemy.x + int(self.hitDistance*0.9)
        else:
            furthestX = self.minX
        if self.position == "stand":
            self.switchAnim("walk")
            self.x -= self.walk_speed
            self.x = max(self.x, furthestX)
            self.flipped = True

    def block(self):
        if self.position == "stand":
            self.blocking = self.block_time
            self.switchAnim("block")
        elif self.position == "crouch":
            self.blocking = self.block_time
            self.switchAnim("crouch_block")

    def punch(self):
        if self.position == "stand":
            self.switchAnim("punch")
        elif self.position == "crouch":
            self.switchAnim("crouch_punch")
        elif self.position == "jump":
            self.switchAnim("jump_punch")
        if self.canHit():
            self.enemy.get_hit(self.punch_damage)

    def canHit(self):
        # I can hit you when:
        # 1) I am within range of a hit
        # 2a) you are standing, I'm crouching
        # 2b) you are jumping, I'm standing
        # 2c) we are both standing, crouching or jumping
        # 3) you are facing the opponent

        correct_distance = abs(self.getDist()) <= self.hitDistance

        correct_position = ((self.position == "crouch" and self.enemy.position == "standing")
                            or (self.position == "standing" and self.enemy.position == "jump")
                            or (self.position == self.enemy.position))

        correct_facing = (
                (self.x <= self.enemy.x and not self.flipped)
                or (self.x >= self.enemy.x and self.flipped)
        )

        return correct_distance and correct_position and correct_facing

    def getDist(self):
        return self.enemy.getPos()[0] - self.getPos()[0]

    def jump(self):
        if self.y_offset == 0 and self.position == "stand":
            self.jump_speed_now = self.jump_speed
            self.switchAnim("jump")
            self.position = "jump"

    def crouch(self):
        if self.y_offset == 0 and self.position == "stand":
            self.switchAnim("crouch")
            self.position = "crouch"

    def stand(self):
        if self.y_offset == 0 and self.position == "crouch":
            self.switchAnim("idle")
            self.position = "stand"

    def get_hit(self, damage):
        if self.blocking > 0:
            pass #ignore damage while blocking
        else:
            self.timeout = self.timeout_time_get_hit
            self.health -= damage
            if self.health > 0:
                if self.position == "crouch":
                    self.switchAnim("crouch_hit")
                elif self.position == "stand":
                    self.switchAnim("hit")
                elif self.position == "jump":
                    self.switchAnim("jump_hit")
            else:
                self.switchAnim("knockdown")
                self.disabled = True

    def switchAnim(self, anim):
        anim = anim.lower()
        if self.current_anim != anim:
            self.key = 0
            self.current_anim = anim

    def setEnemy(self, other):
        self.enemy = other

    def getEnemy(self):
        return self.enemy

    def isFlipped(self):
        return self.flipped

    def addAnimation(self, name, images):
        self.animations[name.lower()] = images

    def getImage(self):
        series = self.animations.get(self.current_anim.lower())
        img = series[self.key]
        self.key += 1
        if self.key >= len(series):
            if self.current_anim.lower() == "knockdown" or self.current_anim.lower() == "victory":
                self.key = len(series) - 1
            elif "block" in self.current_anim.lower():
                self.key = len(series) - 1
            elif "punch" in self.current_anim.lower() or "hit" in self.current_anim.lower():
                if "crouch" in self.current_anim.lower():
                    self.switchAnim("crouch")
                if "jump" in self.current_anim.lower():
                    self.switchAnim("jump")
                else:
                    self.switchAnim("idle")
            else:
                self.key = 0
        return img

    def setState(self, state):
        self.current_anim = state
        self.key = 0

    def createAnimations(self, basepath):
        print("Loading animations for {}".format(self.name))
        folders = os.path.join(basepath, "animations", "*")
        paths = glob.glob(folders)
        d = {}
        for path in paths:
            animation = os.path.split(path)[-1]
            images = animate.get_animation_images(path)
            d[animation.lower()] = images
        print("Found {} images".format(sum([len(x) for x in d.values()])))
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
