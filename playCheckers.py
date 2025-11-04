from checkers import *
import re

"""
    Example script of checkers.py usage, plays out a game of checkers in the IDE's console

    Main game loop:                                             
        - Machine's turn:                                       
            - Identify best movements through minimax algorithm 
            - If no movements are possible, accept defeat       
            - Move the piece accordingly                        
            - Change turn                                       
            - If player has no pieces, declare victory          
        - Player's turn                                         
            - If no movements are possible, accept defeat       
            - Perform a move via desired input                  
            - Move == extracted by evaluating the board state   
            - Check if move made == legal                       
            - Move the tile accordingly inside the program      
            - Change turn                                       
            - If machine has no pieces, declare victory         
        - Difficulty can be controlled via depth of minimax     
            - Higher depth implies harsher AI (Better movements selection)                   
            - Higher depth increases computing time exp
"""

debug = True # Debug mode
auto = True # AI vs AI
boardSize = 6 # 6 and 8 tested

def GetInput(type: str, message: str):
    """Unified function to obtain different types of input from the user

    Args:
        type (str): Type of input to be detected
        message (str): Message to display

    Returns:
        any: Input returned
    """
    userInput = input(message)
    if type == "int":
        if userInput.isnumeric():
            return int(userInput)
        else:
            input(yellow + "Invalid input, press enter to try again" + white)
            return GetInput(type, message)
    elif type == "str":
        return userInput
    elif type == "list":
        inputPos = re.findall(r'\d+', userInput)
        inputPos = [int(x) for x in inputPos]
        if len(inputPos) != 2:
            input(yellow + "Invalid input, press enter to try again" + white)
            return GetInput(type, message)
        inputPos[0] -= 1
        return inputPos
    
gameBoard = Board(0, boardSize, 1, debug)

def Main():
    """Main game loop"""
    if gameBoard.turn == 0:
        gameBoard.SetBoard(debug)
        print("Welcome to PythonCheckers:")
        gameBoard.difficulty = GetInput("int", "Please select your difficulty (1 to 5): \n")
        Main()
    else:
        if gameBoard.turn == 1 and not auto:
            if gameBoard.IsCheckmate(debug) or gameBoard.IsStalemate(debug=debug):
                print("Game has ended, the AI wins")
                gameBoard.turn = 0
                Main()
            print(gameBoard)
            inputPos = GetInput("list", "Which tile do you want to move? <[↓, →]> \n")
            if not gameBoard.InsideBounds(inputPos, debug=debug):
                input(yellow + "Invalid selection, press enter to try again" + white)
                print(gameBoard)
                Main() 
            inputPos = Tile(inputPos[0], inputPos[1])
            posMoves = gameBoard.PossibleMovements(inputPos, debug)
            if len(posMoves[1]) == 0:
                input(yellow + "Invalid selection, press enter to try again" + white)
                print(gameBoard)
                Main() 
            print(posMoves[0])
            inputTarget = GetInput("int", "Which movement do you want to make? <Number> \n")
            inputTarget -= 1
            if inputTarget not in range(len(posMoves[1])):
                input(yellow + "Invalid selection, press enter to try again" + white)
                print(gameBoard)
                Main()
            movement = posMoves[1][inputTarget] 
            if gameBoard.ValidateMovement(movement, debug):
                gameBoard.MoveTile(movement, debug=debug)
                gameBoard.ChangeTurn(debug)
                print(gameBoard)
                Main() 
            else:
                input(yellow + "Internal error, press enter to try again" + white)
                print(gameBoard)
                Main() 
        else:
            if gameBoard.IsCheckmate(debug) or gameBoard.IsStalemate(debug=debug):
                if auto:
                    print(f"Game has ended, player {gameBoard.turn} wins")
                else:
                    print("Game has ended, the player wins")
                gameBoard.turn = 0
                Main()
            movement = MiniMax(gameBoard, debug=debug)
            gameBoard.MoveTile(movement[0], debug=debug)
            gameBoard.ChangeTurn(debug)
            print(gameBoard)
            if auto:
                input("Press enter to advance to the next turn.")
                print("Calculating...")
            Main()
Main()