# some variables to help you
HIT_DISTANCE = 100  # how close you have to be to hit
WALK_DISTANCE = 30  # how far you move when you walk

def your_function_here(your_info, enemy_info, options)
    """
    Change this function to run your bot.
    """

    # returns a sample action from the currently available options.
    options.sample
end

def run()
    """
    Please do not change this function, as it handles the
    way that the game communicates with your fighter.
    Any changes you make here could result in a timeout.
    """

    # receive information about your fighter
	x1, y1, facing1, state1, anim1, health1, ready1 = gets.split(" ")
	your_info = [x1, y1, facing1, state1, anim1, health1, ready1]

    # receive information about the enemy fighter
	x2, y2, facing2, state2, anim2, health2, ready2 = gets.split(" ")
	enemy_info = [x2, y2, facing2, state2, anim2, health2, ready2]

    # your available options to choose from
    options = gets.split(" ")

    # the choice made by your bot
    output = your_function_here(your_info, enemy_info, options)

    # output a response
	puts output
	STDOUT.flush
end

# your bot's main loop
while true
	run()
end