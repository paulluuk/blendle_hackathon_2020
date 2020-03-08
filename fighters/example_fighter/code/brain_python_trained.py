import random

# some variables to help you
HIT_DISTANCE = 100  # how close you have to be to hit
WALK_DISTANCE = 30  # how far you move when you walk


def within_range(your_position, enemy_position):
    """Am I close enough to hit my enemy?"""
    return abs(your_position - enemy_position) <= HIT_DISTANCE


def facing_enemy(your_position, enemy_position, your_facing):
    """Am I turned towards my enemy?"""
    return (
            (your_position <= enemy_position and your_facing == "right")
            or
            (your_position >= enemy_position and your_facing == "left")
    )


def try_one_of(given_list, available_list):
    # tries to return one of the actions in the given list,
    # if they're not available, returns None
    for option in given_list:
        if option in available_list:
            return option


def punch(available_options):
    return try_one_of(["punch", "crouch_punch", "jump_punch"], available_options)


def block(available_options):
    return try_one_of(["block", "crouch_block"], available_options)


def bot_runner(your_info, enemy_info, options):
    """
    Change this function to run your bot.
    """
    x1, y1, facing1, state1, anim1, health1, i_am_ready = your_info
    x2, y2, facing2, state2, anim2, health2, enemy_is_ready = enemy_info

    if not i_am_ready:
        # you're not ready to do anything
        # the game will ignore whatever you send back
        return "ZZZzzz.. ZZZzzz.. ZZZzzz..."

    if facing_enemy(x1, x2, facing1) and within_range(x1, x2):

        if enemy_is_ready and facing_enemy(x2, x1, facing2):  # the enemy is facing me and ready to hit
            action = block(options)
            if action is not None:
                return action
        else:
            action = punch(options)
            if action is not None:
                return action
    else:

        if x1 < x2 and "walk_right" in options:
            return "walk_right"
        elif x1 > x2 and "walk_left" in options:
            return "walk_left"

    # if I reached this code, then I did nothing.
    # I guess I'll just do a random action then.
    return random.choice(options)


def run():
    """
    Please do not change this function, as it handles the
    way that the game communicates with your fighter.
    Any changes you make here could result in a timeout.
    """

    # receive information about your fighter
    x1, y1, facing1, state1, anim1, health1, ready1 = input().split(" ")
    your_info = (int(x1), int(y1), facing1, state1, anim1, int(health1), bool(ready1 == "True"))

    # receive information about the enemy fighter
    x2, y2, facing2, state2, anim2, health2, ready2 = input().split(" ")
    enemy_info = (int(x2), int(y2), facing2, state2, anim2, int(health2), bool(ready2 == "True"))

    # your available options to choose from
    options = input().split(" ")

    # randomly choose one of the available options
    data_out = bot_runner(your_info, enemy_info, options)

    # output a response
    print(data_out, flush=True)


# your bot's main loop
while True:
    run()
