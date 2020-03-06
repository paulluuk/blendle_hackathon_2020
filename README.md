# Blendle Hackfest 2020
###who can program the best fighter?
This project puts fighters together to fight eachother.
The fighters are given some information about themselves and their opponents,
and they have to use this information to defeat their enemies.

Every contestant will have to submit (at least) one AI fighter,
which they wrote themselves, to challenge eachother for domination in this championship.

## To run the project
I recommend to create a virtualenv by running:
```
pip install virtualenv
python -m venv venv
venv\script\activate
pip install -r requirements.txt
```
Then, to run the project, simply run:
```
python run.py
```

The game requires that there is at least one fighter available in the fighters folder.
Each fighter should come with animations, at least one background, and a "brain".
The "example_fighter" can be used as a template for the creation of a new, better fighter.
