from checkers import *

#################################################################
#   Main game loop:                                             #
#       - Machine's turn:                                       #
#           - Identify best movements through minimax algorithm #
#           - If no movements are possible, accept defeat       #
#           - Move the piece accordingly                        #
#           - Change turn                                       #
#           - If player has no pieces, declare victory          #
#       - Player's turn                                         #
#           - If no movements are possible, accept defeat       #
#           - Perform a move via desired input                  #
#           - Move is extracted by evaluating the board state   #
#           - Check if move made is legal                       #
#           - Move the tile accordingly inside the program      #
#           - Change turn                                       #
#           - If machine has no pieces, declare victory         #
#       - Difficulty can be controlled via depth of minimax     #
#           - Higher depth implies harsher AI                   #
#           - Higher depth increases computing time exp         #
#   Optionally:                                                 #
#       - Implement stalemate rules on main code                #
#################################################################

gameBoard = Board(0)
minimax = Minimax()
difficulty = 3
stale = 0
totalCount = 12

def GetInputPos(msg):
    inputPos = input(msg)
    inputPos = [int(x) for x in inputPos.split() if x.isnumeric()]
    if len(inputPos) != 2:
        return [-1, -1]
    for i in inputPos:
        if not 0 <= i <= 5:
            return [-1, -1]
    return inputPos
def Main():
    global stale, totalCount, difficulty
    if gameBoard.turn == 0:
        gameBoard.SetBoard()
        gameBoard.turn = 1
        stale = 0
        totalCount = 12
        print(gameBoard)
        print("Welcome to PythonCheckers:")
        difficulty = int(input("Please select your difficulty (1 to 5): \n"))
        Main()
    else:
        if gameBoard.turn == 1:
            if gameBoard.GetAmmountOf(gameBoard.turn) == 0 and gameBoard.GetAmmountOf(gameBoard.turn * 2) == 0:
                input(f"Player {gameBoard.turn} has lost, press enter to restart")
                gameBoard.turn = 0
                Main()
            movement = minimax.MiniMax(gameBoard, 1)
            if movement[0] == Movement([0, 0]) or stale > 10:
                input(f"Player {gameBoard.turn} has lost by stalemate, press enter to restart")
                gameBoard.turn = 0
                Main()
            if totalCount != gameBoard.GetAmmountOf(gameBoard.turn) + gameBoard.GetAmmountOf(gameBoard.turn + 1):
                totalCount = gameBoard.GetAmmountOf(gameBoard.turn) + gameBoard.GetAmmountOf(gameBoard.turn + 1)
                stale = 0
            else:
                stale += 1
            inputPos = GetInputPos("Which tile do you want to move (x  y)? \n")
            inputTarget = GetInputPos("Where do you want to move (x  y)? \n")
            movement = Movement(inputPos, [inputTarget])
            if gameBoard.ValidateMovement(movement):
                gameBoard.MoveTile(movement)
                gameBoard.ChangeTurn()
                print(gameBoard)
                Main()
            else:
                input("Invalid movement, press enter to try again")
                Main()
        else:
            if gameBoard.GetAmmountOf(gameBoard.turn) == 0 and gameBoard.GetAmmountOf(gameBoard.turn * 2) == 0:
                input(f"Player {gameBoard.turn} has lost, press enter to restart")
                gameBoard.turn = 0
                Main()
                print(difficulty)
            movement = minimax.MiniMax(gameBoard, difficulty)
            if movement[0] == Movement([0, 0]) or stale > 10:
                input(f"Player {gameBoard.turn} has lost by stalemate, press enter to restart")
                gameBoard.turn = 0
                Main()
            if totalCount != gameBoard.GetAmmountOf(gameBoard.turn) + gameBoard.GetAmmountOf(gameBoard.turn + 1):
                totalCount = gameBoard.GetAmmountOf(gameBoard.turn) + gameBoard.GetAmmountOf(gameBoard.turn + 1)
                stale = 0
            else:
                stale += 1
            gameBoard.MoveTile(movement[0])
            gameBoard.ChangeTurn()
            print(gameBoard)
            Main()
Main()
