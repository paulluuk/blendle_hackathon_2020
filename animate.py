import glob
import os

from PIL import Image


def convert_alpha(img):
    width, height = img.size
    pixdata = img.load()
    colorkey = pixdata[0, 0]
    shadow = (64, 32, 0)
    for y in range(height):
        for x in range(width):
            if pixdata[x, y][:3] == colorkey[:3]:
                pixdata[x, y] = (colorkey[0], colorkey[1], colorkey[2], 0)
            elif pixdata[x, y][:3] == shadow:
                pixdata[x, y] = (0, 0, 0, 100)
    return img


def get_animation_images(anim_path):
    folder = os.path.join(anim_path, "*.png")
    paths = glob.glob(folder)
    return [convert_alpha(resize_image(load_image(i), 200, 200)) for i in sorted(paths)]


def resize_image(img, xx, yy):
    return img.resize((xx, yy), Image.NEAREST)


def load_image(path):
    return Image.open(path).convert("RGBA")


def animate_sequence(images, name):
    # make the images much smaller before saving them
    width, height = images[0].size
    height_per_width = 100 * height / width
    desired_width = 700
    images = [
        resize_image(image, desired_width, int(height_per_width * desired_width / 100))
        for image in images
    ]

    steps = os.path.split(name)
    path = ""
    for step in steps[:-1]:
        path = os.path.join(path, step)
        if not os.path.exists(path):
            os.mkdir(path)
    images[0].save(name, save_all=True, append_images=images[1:], duration=75, loop=1)


def place_on_background(background, img, x, y):
    copy = background.copy()
    copy.paste(img, (x, y), mask=img)
    return copy


def flip(image):
    return image.transpose(Image.FLIP_LEFT_RIGHT)
