import glob
import os

import pygame


def convert_alpha(img):
    width, height = img.get_size()
    colorkey = img.get_at((0, 0))
    shadow = (64, 32, 0)
    for y in range(height):
        for x in range(width):
            if img.get_at((x, y))[:3] == colorkey[:3]:
                img.set_at((x, y), (colorkey[0], colorkey[1], colorkey[2], 0))
            elif img.get_at((x, y))[:3] == shadow:
                img.set_at((x, y), (0, 0, 0, 100))
    return img


def load_image(path):
    return pygame.image.load(path).convert_alpha()


def get_animation_images(anim_path):
    folder = os.path.join(anim_path, "*.png")
    paths = glob.glob(folder)
    return [convert_alpha(resize_image(load_image(i), 200, 200)) for i in sorted(paths)]


def resize_image(img, xx, yy):
    return pygame.transform.scale(img, (xx, yy))


# test
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((300, 300))
    path = os.path.join("fighters", "example_fighter", "animations", "hit")

    imgs = get_animation_images(path)
    pygame.image.save(imgs[0], "tmp.png")
