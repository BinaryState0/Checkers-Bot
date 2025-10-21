# Checkers-Bot
## About
This python library provides tools for creating a program which can physically play checkers against a human. This is done by using the cv2 library to analize IRL movements and playing them in a virtual board against a minimax algorithm
## Files
### checkers.py
This script provides 3 classes that can be used to create a fully functioning 6x6 game of checkers
### playCheckers.py
This script provides a fully functioning game of checkers through the console, for testing checkers.py
### detection.py
This script provides various functions to help capture and analize movements through a provided image, depends on checkers.py
## How to use
### Writing a main script
You can base off of playCheckers.py to create a main script, using detection.py replace the player's input with an automated capture via the provided functions and the AI's output with your own control method with which the machine performs movements in real life
### Things to consider
- Higher depths for the minimax algorithm increase the calculation time exponentally, a maximum value of 5 is recommended but 3 will be enough in most cases
- This library does not provide any tools to move a robot or capture images
