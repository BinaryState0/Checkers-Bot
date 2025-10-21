from checkers import *
import re

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
#           - Move == extracted by evaluating the board state   #
#           - Check if move made == legal                       #
#           - Move the tile accordingly inside the program      #
#           - Change turn                                       #
#           - If machine has no pieces, declare victory         #
#       - Difficulty can be controlled via depth of minimax     #
#           - Higher depth implies harsher AI                   #
#           - Higher depth increases computing time exp         #
#   Optionally:                                                 #
#       - Implement stalemate rules on main code                #
#################################################################

gameBoard = Board(0) #Create empty board
minimax = Minimax() #Initialize minimax class
difficulty = 3 #Global variables
stale = 0
totalCount = 12

def GetInputPos(msg): #Returns coordinates from input or a default case if invalid
    inputPos = input(msg) #Obtain input
    inputPos = re.findall(r'\d+', inputPos) #Extract numbers
    inputPos = [int(x) for x in inputPos]
    if len(inputPos) != 2: #If not 2 numbers, return default
        return [-1, -1]
    inputPos[0] -= 1
    return inputPos
def Main(): #Main game loop
    global stale, totalCount, difficulty #Initializae global variables
    if gameBoard.turn == 0: #If turn == 0 (Game ended)
        gameBoard.SetBoard() #Set board for new game
        gameBoard.turn = 1 #Set initial turn
        stale = 0 #Reset stalemate count
        totalCount = 12 #Reset tiles count
        print(gameBoard) #Print initial board
        print("Welcome to PythonCheckers:")
        difficulty = input("Please select your difficulty (1 to 5): \n") #Difficulty selection
        if difficulty.isnumeric():
            difficulty = int(difficulty)
        else:
            input(yellow + "Invalid selection, press enter to try again" + white)
            gameBoard.turn = 0
        Main() #Loop
    else:
        if gameBoard.turn == 1: #If player turn
            if gameBoard.GetAmmountOf(gameBoard.turn) == 0 and gameBoard.GetAmmountOf(gameBoard.turn * 2) == 0:
                input(f"Player {gameBoard.turn} has lost, press enter to restart")
                gameBoard.turn = 0
                Main() #Loss by losing all pieces
            movement = minimax.MiniMax(gameBoard, 1)
            if movement[0] == Movement([0, 0]) or stale > 10:
                input(f"Player {gameBoard.turn} has lost by stalemate, press enter to restart")
                gameBoard.turn = 0
                Main() #Loss by stalemate
            if totalCount != gameBoard.GetAmmountOf(gameBoard.turn) + gameBoard.GetAmmountOf(gameBoard.turn + 1):
                totalCount = gameBoard.GetAmmountOf(gameBoard.turn) + gameBoard.GetAmmountOf(gameBoard.turn + 1)
                stale = 0 
            else:
                stale += 1 #Check for stalemate
            inputPos = GetInputPos("Which tile do you want to move? <v, h> \n") #Get position [x, y] for movement start
            if not gameBoard.InsideBounds(inputPos):
                input(yellow + "Invalid selection, press enter to try again" + white)
                print(gameBoard)
                Main() #Loop
            posMoves = gameBoard.PossibleMovements(inputPos)
            print(posMoves[0])
            inputTarget = input("Which movement do you want to make? <n> \n") #Get movement index
            if inputTarget.isnumeric():
                inputTarget = int(inputTarget) - 1
                if inputTarget > len(posMoves[1]) - 1:
                    input(yellow + "Invalid selection, press enter to try again" + white)
                    print(gameBoard)
                    Main() #Loop 
            else:
                input(yellow + "Invalid selection, press enter to try again" + white)
                print(gameBoard)
                Main() #Loop
            if posMoves[1][inputTarget] is not None:
                movement = posMoves[1][inputTarget] 
                if gameBoard.ValidateMovement(movement): #Validate movement
                    gameBoard.MoveTile(movement) #Attempt movement
                    gameBoard.ChangeTurn() #Change turn
                    print(gameBoard) #Print current board
                    Main() #Loop
                else: #If invalid
                    input(yellow + "Internal error, press enter to try again" + white)
                    print(gameBoard)
                    Main() #Loop
            else:
                input(yellow + "Invalid movement, press enter to try again" + white)
                print(gameBoard)
                Main() #Loop
        else:
            if gameBoard.GetAmmountOf(gameBoard.turn) == 0 and gameBoard.GetAmmountOf(gameBoard.turn * 2) == 0:
                input(f"Player {gameBoard.turn} has lost, press enter to restart")
                gameBoard.turn = 0
                Main() #Loss by losing all pieces
            movement = minimax.MiniMax(gameBoard, difficulty) #Get minimax movement with depth difficulty
            print(yellow + f"Debug: found movement {movement[0]} with score {abs(movement[1])} for AI" + white)
            if movement[0] == Movement([-1, -1]) or stale > 10:
                input(f"Player {gameBoard.turn} has lost by stalemate, press enter to restart")
                gameBoard.turn = 0
                Main() #Loss by stalemate
            if totalCount != gameBoard.GetAmmountOf(gameBoard.turn) + gameBoard.GetAmmountOf(gameBoard.turn + 1):
                totalCount = gameBoard.GetAmmountOf(gameBoard.turn) + gameBoard.GetAmmountOf(gameBoard.turn + 1)
                stale = 0
            else:
                stale += 1 #Check for stalemate
            gameBoard.MoveTile(movement[0]) #Make movement
            gameBoard.ChangeTurn() #Change turn
            print(gameBoard) #Print board
            Main() #Move
Main()
