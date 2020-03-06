def run():

    # receive information about your fighter
    x1, y1, state1, anim1, health1, ready1 = input().split(" ")

    # receive information about the enemy fighter
    x2, y2, state2, anim2, health2, ready2 = input().split(" ")

    # do something with the data_in
    data_out = 'punch'

    # output a response
    print(data_out, flush=True)


while True:
    run()
