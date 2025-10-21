from checkers import *
from detection import *

redColor = Color(0, 255, 255)
pinkColor = Color(150, 255, 255)
orangeColor = Color(20, 255, 255)

board = Board()
otherBoard = Board()

frame1 = cv2.imread('Frame1.jpg')
frame2 = cv2.imread('Frame2.jpg')

board.board = Detection.ReadBoard(frame1, pinkColor, orangeColor, redColor)
print(board)

otherBoard.board = Detection.ReadBoard(frame2, pinkColor, orangeColor, redColor)
print(otherBoard)

movement = board.ExtractMovement(otherBoard)

print(movement)