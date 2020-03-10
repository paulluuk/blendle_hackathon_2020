import glob
import os

import cv2
import numpy
from PIL import Image, ImageOps
from cv2.cv2 import cvtColor, COLOR_RGB2BGR, COLOR_BGR2RGB

DIR = os.path.dirname(__file__)


def get_camera():
    # This can sometimes throw the error "Abort trap: 6"
    # if that happens, try to change the type of terminal
    # you're using. It doesn't work from my IDE, for example.
    return cv2.VideoCapture(0)


def capture_image(cam, path, num, save=True):
    _, frame = cam.read()
    frame = cvtColor(frame, COLOR_BGR2RGB)
    im = Image.fromarray(frame, "RGB")
    w, h = im.width, im.height
    height_per_width = float(h) / float(w)
    desired_width = min(400, w)
    im = im.resize(
        (desired_width, int(desired_width * height_per_width)), resample=Image.NEAREST
    )
    im = ImageOps.fit(im, (400, 400), Image.NEAREST)
    if save:
        im.save(os.path.join(path, str(num) + ".png"), "PNG")
    return frame


def load_preview_images(anim):
    path = os.path.join(DIR, "helpers", anim, "*.png")
    files = glob.glob(path)
    preview_images = []
    for file in files:
        preview_images += [load_8bit_resized(file)]
    return preview_images


def clear_folder(path):
    os.makedirs(path, exist_ok=True)
    files = glob.glob(os.path.join(path, "*.png"))
    for file in files:
        print("deleting {}".format(file))
        os.remove(file)
    files = glob.glob(os.path.join(path, "cleaned", "*.png"))
    for file in files:
        print("deleting {}".format(file))
        os.remove(file)


def remove_background(image, bg, sensitivity=25):
    img = load_8bit_resized(image)
    output_image = Image.new("RGBA", img.size, (0, 0, 0, 0))

    for x in range(img.width):
        for y in range(img.height):
            r1, g1, b1, a1 = img.getpixel((x, y))
            r2, g2, b2, a2 = bg.getpixel((x, y))
            if (
                abs(r1 - r2) < sensitivity
                and abs(g1 - g2) < sensitivity
                and abs(b1 - b2) < sensitivity
            ):
                pass
            else:
                output_image.putpixel((x, y), (r1, g1, b1, 255))

    return output_image


def clean_background_from_dir(bg_image, anim_path):
    os.makedirs(os.path.join(os.path.dirname(anim_path), "cleaned"), exist_ok=True)
    files = glob.glob(anim_path)
    for file_path in files:
        cleaned = remove_background(file_path, bg_image)
        newpath = os.path.dirname(file_path)
        filename = os.path.basename(file_path)
        cleaned.save(os.path.join(newpath, "cleaned", filename))
        print("cleaned {}".format(file_path))


def load_8bit_resized(path, image=None):
    if not image:
        img = Image.open(path).convert("RGB").resize((400, 400), Image.NEAREST)
    else:
        img = image.convert("RGB").resize((400, 400))
    img = ImageOps.posterize(img, 2)
    return img.convert("RGBA")


def blend_array_images(frame, img):
    return numpy.array(
        Image.blend(
            load_8bit_resized(path=None, image=img),
            load_8bit_resized(path=None, image=Image.fromarray(frame)),
            0.2,
        )
    )


def writeOnImage(image, text, size):
    font = cv2.FONT_HERSHEY_SIMPLEX
    x, y = size
    pos = (int(x * 0.2), int(y * 0.7))
    fontScale = 1
    fontColor = (255, 255, 255)
    lineType = 2

    cv2.putText(image, text, pos, font, fontScale, fontColor, lineType)


def run():
    anims = [
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
    ]

    time_instruction = 80
    time_wait = 50
    time_camera = 10
    cancel = False
    window_name = "Capturing.."

    # start camera
    cam = get_camera()

    # start fullscreen window
    cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    for anim in anims:
        i = 0
        path = os.path.join(DIR, "captured", anim)
        clear_folder(path)
        preview_images = load_preview_images(anim)

        #### INSTRUCTIONS #####
        idx = 0
        for _ in range(time_instruction):
            img = cvtColor(numpy.array(preview_images[idx]), COLOR_RGB2BGR)
            writeOnImage(img, anim, preview_images[idx].size)
            cv2.imshow(window_name, img)
            idx += 1
            if idx >= len(preview_images):
                idx = 0
            if cv2.waitKey(10) == ord("q"):
                cancel = True
                break
        if cancel:
            break

        ### GET READY! ####
        img = load_8bit_resized(os.path.join(DIR, "helpers", "get_ready.png"))

        for _ in range(time_wait):
            frame = capture_image(cam, path, 0, False)
            writeOnImage(frame, anim, preview_images[-1].size)
            cv2.imshow(
                window_name,
                cvtColor(
                    blend_array_images(
                        blend_array_images(frame, img), preview_images[-1]
                    ),
                    COLOR_RGB2BGR,
                ),
            )
            if cv2.waitKey(10) == ord("q"):
                cancel = True
                break
        if cancel:
            break

        ### GO! ###
        while i < time_camera:
            frame = capture_image(cam, path, i)
            cv2.imshow(
                window_name,
                cvtColor(blend_array_images(frame, preview_images[-1]), COLOR_RGB2BGR),
            )
            i += 1
            if cv2.waitKey(10) == ord("q"):
                cancel = True
                break
        if cancel:
            break

    ### PROCESSING.. ###
    img = load_8bit_resized(os.path.join(DIR, "helpers", "processing.png"))
    cv2.imshow(window_name, cvtColor(numpy.array(img), COLOR_RGB2BGR))
    cam.release()
    cv2.destroyAllWindows()

    for anim in anims[1:]:  # skip cleaning background images
        anim_path = os.path.join(DIR, "captured", anim, "*.png")
        bg_path = os.path.join(
            DIR, "captured", "nothing", "{}.png".format(str(time_camera - 1))
        )
        bg = load_8bit_resized(bg_path)
        clean_background_from_dir(bg, anim_path)


if __name__ == "__main__":
    run()
    # time_camera = 10
    # anim = "block"
    # anim_path = os.path.join(DIR, "captured", anim, "*.png")
    # bg_path = os.path.join(
    #     DIR, "captured", "nothing", "{}.png".format(str(time_camera - 1))
    # )
    # bg = load_8bit_resized(bg_path)
    # clean_background_from_dir(bg, anim_path)
