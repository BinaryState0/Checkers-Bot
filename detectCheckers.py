from checkers import *
from detection import *

redColor = Color(0, 255, 255)
pinkColor = Color(150, 255, 255)
orangeColor = Color(20, 255, 255)

board = Board()
otherBoard = Board()

frame1 = cv2.imread('Frame1.jpg')
frame2 = cv2.imread('Frame2.jpg')

coords = Detection.FindBoardCoords(frame1, redColor)

board.board = Detection.ReadBoard(frame1, pinkColor, orangeColor, coords, debug=True)

otherBoard.board = Detection.ReadBoard(frame2, pinkColor, orangeColor, coords, debug=True)

movement = board.FindMovement(otherBoard, debug=True)
print(movement)