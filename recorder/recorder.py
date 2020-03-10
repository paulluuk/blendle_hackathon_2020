import glob
import os

import cv2
import numpy
from PIL import Image

DIR = os.path.dirname(__file__)


def get_camera():
    return cv2.VideoCapture(0)


def capture_image(cam, path, num):
    _, frame = cam.read()
    im = Image.fromarray(frame, "RGB")
    im = im.resize((500, 500))
    im.save(os.path.join(path, str(num) + ".png"), "PNG")
    return frame


def load_preview_images(anim):
    path = os.path.join(DIR, "helpers", anim, "*.png")
    files = glob.glob(path)
    preview_images = []
    for file in files:
        preview_images += [load_image(file)]
    return preview_images


def load_image(path):
    return numpy.array(
        Image.open(path).convert("RGB").resize((500, 500), Image.NEAREST)
    )


def run():
    cam = get_camera()

    for anim in [
        "nothing",
        "block",
        "crouch",
        "crouch_block",
        "crouch_hit",
        "crouch_punch",
        "hit",
        "idle",
        "jump",
        "jump_hit",
        "jump_punch",
        "knockdown",
        "punch",
        "victory",
        "walk",
    ]:
        i = 0
        path = os.path.join(DIR, "captured", anim)
        os.makedirs(path, exist_ok=True)
        preview_images = load_preview_images(anim)
        cancel = False
        print(len(preview_images))
        for _ in range(100):
            cv2.imshow("Capturing", preview_images[idx])
            idx += 1
            if idx >= len(preview_images):
                idx = 0
            if cv2.waitKey(10) == ord("q"):
                cancel = True
                break
        if cancel:
            break

        img = load_image(os.path.join(DIR, "helpers", "get_ready.png"))

        for _ in range(100):
            cv2.imshow("Capturing", img)
            if cv2.waitKey(10) == ord("q"):
                cancel = True
                break
        if cancel:
            break
        while i < 100:
            frame = capture_image(cam, path, i)
            cv2.imshow("Capturing", frame)
            i += 1
            if cv2.waitKey(10) == ord("q"):
                cancel = True
                break
        if cancel:
            break

    cam.release()


if __name__ == "__main__":
    run()
