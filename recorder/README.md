# Fighter Recorder
### Automatically capture your own fighter animations
Each fighter in this game has their own appearance.
You can create your own by getting sprites from the internet, or by painting them yourself.
But you can also use this tool to automatically record them using your laptop's webcam.

In order to run this, type
`python recorder.py`
while you are in the folder of this readme file.

You will be shown examples of the animation that it will record,
and then you have to copy that animation in front of the camera.

The first "animation" will be an empty frame. For this one,
make sure that only the background is visible in the image.
The script will learn that it needs to treat that background as the "greenscreen".
Do not change your laptop's position between animations,
because that will make it impossible for the camera to greenscreen your animations.