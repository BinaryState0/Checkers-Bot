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

gameBoard = Board(0) #Create empty board
minimax = Minimax() #Initialize minimax class
difficulty = 3 #Global variables
stale = 0
totalCount = 12

def GetInputPos(msg): #Returns coordinates from input or a default case if invalid
    inputPos = input(msg) #Obtain input
    inputPos = [int(x) for x in inputPos.split() if x.isnumeric()] #Extract numbers
    if len(inputPos) != 2: #If not 2 numbers, return default
        return [-1, -1]
    for i in inputPos: #For each number
        if not 0 <= i <= 5: #If not inside bounds, return default
            return [-1, -1]
    return inputPos
def Main(): #Main game loop
    global stale, totalCount, difficulty #Initializae global variables
    if gameBoard.turn == 0: #If turn is 0 (Game ended)
        gameBoard.SetBoard() #Set board for new game
        gameBoard.turn = 1 #Set initial turn
        stale = 0 #Reset stalemate count
        totalCount = 12 #Reset tiles count
        print(gameBoard) #Print initial board
        print("Welcome to PythonCheckers:") 
        difficulty = int(input("Please select your difficulty (1 to 5): \n")) #Difficulty selection
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
            inputPos = GetInputPos("Which tile do you want to move <x  y>? \n") #Get position [x, y] for movement start
            inputTarget = GetInputPos("Where do you want to move <x  y>? \n") #Get position [x, y] for movement ending
            movement = Movement(inputPos, [inputTarget]) #Initialize coords as a movement TODO: implement multiple jumps
            if gameBoard.ValidateMovement(movement): #Validate movement
                gameBoard.MoveTile(movement) #Attempt movement
                gameBoard.ChangeTurn() #Change turn
                print(gameBoard) #Print current board
                Main() #Loop
            else: #If invalid
                input("Invalid movement, press enter to try again")
                Main() #Loop
        else:
            if gameBoard.GetAmmountOf(gameBoard.turn) == 0 and gameBoard.GetAmmountOf(gameBoard.turn * 2) == 0:
                input(f"Player {gameBoard.turn} has lost, press enter to restart")
                gameBoard.turn = 0
                Main() #Loss by losing all pieces
            movement = minimax.MiniMax(gameBoard, difficulty) #Get minimax movement with depth difficulty
            if movement[0] == Movement([0, 0]) or stale > 10:
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
