import copy 
import random

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

#Color codes for console output
red = "\033[31m"
blue = "\033[34m"
white = "\033[37m"

class Board:
    def __init__(self, turn = 1): #Initiates board
        self.board = [[0 for _ in range(8)] for _ in range(6)] # 6x8 Array of 0s
        self.turn = turn
        self.turnCount = 1
    def __str__(self): #Converts board to a string
        if self.turn == 1:
            boardStr = "Turn: " + str(self.turnCount) + " | " + blue + "Blue moves" + white + "\n"
        else:
            boardStr = "Turn: " + str(self.turnCount) + " | "  + red + "Red moves" + white + "\n"
        boardStr += "  x | ➀ ➁ ➂ ➃ ➄ ➅ | x" + "\n"
        for i in range(6):
            if i == 0:
                boardStr += "➀ "
            elif i == 1:
                boardStr += "➁ "    
            elif i == 2:
                boardStr += "➂ "
            elif i == 3:
                boardStr += "➃ "
            elif i == 4:
                boardStr += "➄ "
            elif i == 5:
                boardStr += "➅ "
            for j in range(8):
                pos = [i, j]
                tile = self.GetTileAtPos(pos)
                if pos[1] == 7:
                        boardStr += white + "| "
                if tile == 0:
                    boardStr += white + "·"
                elif tile > 0:
                    boardStr += blue
                    if tile == 1:
                        boardStr += "o" #Player 2
                    else:
                        boardStr += "O" #Player 2 king
                    boardStr += white
                else:
                    boardStr += red
                    if tile == -1:
                        boardStr += "ø"	#Player 1
                    else:
                        boardStr += "Ø" #Player 1 king
                    boardStr += white
                if pos[1] == 0:
                    boardStr += white + " |"
                boardStr += " "
            if i == 0:
                boardStr += "➀"
            elif i == 1:
                boardStr += "➁"    
            elif i == 2:
                boardStr += "➂"
            elif i == 3:
                boardStr += "➃"
            elif i == 4:
                boardStr += "➄"
            elif i == 5:
                boardStr += "➅"
            boardStr += "\n"
        boardStr += white
        boardStr += "  x | ➀ ➁ ➂ ➃ ➄ ➅ | x" + "\n"
        return boardStr
    def SetBoard(self): #Resets board
        self.turnCount = 1
        self.turn = 1
        for i, j in [(x, y) for x in range(0, 6) for y in range(0, 6)]:
            j = j + 1
            pos = [i, j]
            if j % 2 == ((i +  1) % 2): #Checks to see if a tile should be there
                if i < 2:
                    self.SetTileAtPos(pos, -1) #Adds player 1
                elif i > 3:
                    self.SetTileAtPos(pos, 1) #Adds player 2
                else: self.SetTileAtPos(pos, 0)
            else: 
                self.SetTileAtPos(pos, 0)
    def GetTileAtPos(self, pos): #Returns the type of tile at i, j
        return self.board[pos[0]][pos[1]]
    def SetTileAtPos(self, pos, type): #Sets the tile at position i, j to type
        self.board[pos[0]][pos[1]] = type
    def GetAmmountOf(self, type): #Returns the ammount of a type of tile in the board
        count = 0
        for i in self.board:
            count += i.count(type)
        return count
    def InsideBounds(self, pos): #Check if a position == inside the game board
        if 0 <= pos[0] <= 5 and 1 <= pos[1] <= 6: #If inside game board
            return True
        else:
            return False
    def MoveTile(self, movement, validate = True): #Swaps tile i1,j1 and i2,j2, kills and converts. If movement == invalid returns False
        iPos = movement.iPos
        if self.ValidateMovement(movement) or not validate: #Validate movement
            for x in range(len(movement.steps)): #For each step
                step = movement.steps[x]
                prevStep = movement.steps[x-1]
                if  (
                        ((step[0] == 0 or 
                        step[0] == 5) and
                        abs(self.GetTileAtPos(step)) != 2) and
                        validate
                    ): #Check for king
                        self.SetTileAtPos(iPos, self.turn * 2)
                if x == 0: #Swap tiles
                    self.board[iPos[0]][iPos[1]], self.board[step[0]][step[1]] = self.board[step[0]][step[1]], self.board[iPos[0]][iPos[1]]
                    direction = [step[0] - iPos[0], step[1] - iPos[1]]
                else:
                    self.board[prevStep[0]][prevStep[1]], self.board[step[0]][step[1]] = self.board[step[0]][step[1]], self.board[prevStep[0]][prevStep[1]]
                    direction = [step[0] - prevStep[0], step[1] - prevStep[1]]
                if abs(direction[0]) == 2 and abs(direction[1]) == 2 and validate: #Piece jumped
                    i = 1 if direction[0] > 0 else -1 if direction[0] < 0 else 0
                    j = 1 if direction[1] > 0 else -1 if direction[1] < 0 else 0
                    direction = [i, j]
                    pos = [iPos[0] + direction[0], iPos[1] + direction[1]] #Get jumped tile position
                    if self.InsideBounds(pos): #Move jumped tile to first unoccupied cemetery slot
                        cPos = [-1, -1]
                        if self.turn == 1:
                            j = 7
                            for i in range(6):
                                if self.GetTileAtPos([i, j]) == 0:
                                    cPos = [i, j]
                                    continue
                        else:
                            j = 0
                            for i in range(6):
                                i = 5 - i
                                if self.GetTileAtPos([i, j]) == 0:
                                    cPos = [i, j]
                                    continue
                        move = Movement(pos, [cPos])
                        self.MoveTile(move, False)
                    else:
                        return False
        else:
            return False
    def GetMovesTable(self): #Returns a 6x6 table of arrays with possible movements for each piece in the turn
        moveSet = [[[] for _ in range(8)] for _ in range(6)] #Empty 6x8 table of arrays
        for i, j in [(x, y) for x in range(0, 6) for y in range(0, 6)]: #For each tile on the board
            iPos = [i, j + 1] #Initial position
            if (self.GetTileAtPos(iPos) == self.turn or self.GetTileAtPos(iPos) == 2 * self.turn): #Checks for current turn
                paths = self.CheckMovement(iPos) #Saves posible paths
                for path in paths: #For each path
                    if path != []: #If not empty
                        movement = Movement(iPos, path) #Saves path as movement
                        moveSet[i][j].append(movement) #Saves movement to array
        return moveSet
    def CheckMovement(self, pos, iPos = None,  path = None, paths = None, visited = None): #Returns an array of possible steps
        if not iPos: #Initialization of l==ts to avoid duplication of values
            iPos = pos
        if not path:
            path = []
        if not paths:
            paths = []
        if not visited:
            visited = []
        for i, j in [(x, y) for x in [-1, 1] for y in [-1, 1]]: #For each direction
            pos2 = [pos[0] + i, pos[1] + j]
            if  (
                    not self.InsideBounds(pos2) or
                    pos2 in visited
                ): #Check if inside bounds
                if (path and path not in paths): # If path not empty or repeated
                    paths.append(path.copy()) # Save it and backtrack
                continue
            if  ( 
                    (abs(self.GetTileAtPos(iPos)) != 2 and i == self.turn) or
                    self.GetTileAtPos(pos2) == self.turn or
                    self.GetTileAtPos(pos2) == self.turn * 2
                ): #Check if not king or same team
                if  (path and path not in paths): # If path not empty or repeated
                    visited.append(pos2)
                    paths.append(path.copy()) # Save it and backtrack
                    path.pop()
                continue
            if (self.GetTileAtPos(pos2) == 0): #Check if unoccupied and first step
                if (path == []):
                    path.append(pos2) #Save it as step and backtrack
                    visited.append(pos2)
                    paths.append(path.copy())
                    path.pop()
                continue
            else: #On the next tile after
                pos3 = [pos2[0] + i, pos2[1] + j]
                if  (
                    not self.InsideBounds(pos3)
                ): #Check if inside bounds
                    if (path and path not in paths): # If path not empty or repeated
                        paths.append(path.copy()) # Save it and backtrack
                        visited.append(pos2)
                    continue
                if (self.GetTileAtPos(pos3) != 0): #Check if occupied
                    if (path and path not in paths): # If path not empty or repeated
                        paths.append(path.copy()) # Save it and backtrack
                        visited.append(pos2)
                    continue
                path.append(pos3) # Save it and backtrack
                if (path and path not in paths): # If path not empty or repeated
                    paths.append(path.copy())
                    visited.append(pos2)
                    paths = self.CheckMovement(pos3, iPos, path, paths, visited) #Continue checking from pos3
                    path.pop() #Backtrack
        return paths
    def ExtractMovementsRaw(self, prevState): #Returns an array of values to indicate piece movements
        movements = [[[] for _ in range(8)] for _ in range(6)] #6x8 board for value storage
        for i, j in [(x, y) for x in range(0, 6) for y in range(0, 8)]: #For each tile
            mov = self.board[i][j] - prevState.board[i][j] #Substract states
            if mov != 0:
                mov = mov / abs(mov) #Normalizes to 1, 0 or -1
            movements[i][j] = mov
        return movements
    def ExtractMovement(self, prevState): #Returns movement between two boards, False if invalid
        #TODO: Currently only checks a full movment, input may have only the last step, need to extrapolate other steps
        movements = self.ExtractMovementsRaw(prevState)
        iPos = []
        tPos = []
        for i, j in [(x, y) for x in range(0, 6) for y in range(0, 6)]: #For each tile
            pos = movements[i][j]
            pos *= self.turn #Player ID -1 (red) == inverted, th== fixes it
            if pos == -1 and not iPos: #If state == -1, movement starts here
                if not iPos: #Checks that it hasnt found another
                    iPos = [i, j]
                else:
                    return False
        for i, j in [(x, y) for x in range(0, 6) for y in range(0, 6)]: #For each tile
            pos = movements[i][j]
            pos *= self.turn
            if pos == 1 and not tPos: #If state == -1, movement starts here
                if not tPos: #Checks that it hasnt found another
                    tPos = [i, j]
                else:
                    return False
        movement = Movement(iPos, [tPos]) #Saves the movement
        return movement
    def ValidateMovement(self, movement): #Checks a movement against possible moves and returns True or False
        paths = self.CheckMovement(movement.iPos) #Get movesTable
        for path in paths: #For each move
            move = Movement(movement.iPos, path)
            if move == movement: #If movement == inside movesTable
                return True #True
        return False
    def CreateClone(self): #Returns an unlinked copy of the board
        boardCopy = copy.deepcopy(self.board)
        return boardCopy
    def ChangeTurn(self): #Changes the current turn of the current board
        self.turnCount += 1
        if self.turn == 0:
            self.turn = 1
        else:
            self.turn *= -1
class Movement:
    def __init__(self, iPos, steps = None): #Initiates with coordinates i, j
        self.iPos = iPos
        self.steps = steps
        if not steps:
            self.steps = []
    def AddStep(self, k, h): #Adds a step to coords k, h
        self.steps.append([k, h])
    def Step(self):
        self.iPos = [self.steps.pop(0)]
    def __eq__(self, other):
        if  not isinstance(other, Movement):
            print(red + "Cannot compare a movement with an another object type" + white)
            return False
        return self.iPos == other.iPos and self.steps == other.steps
    def __repr__(self):
        movStr = "mov(" + str(self.iPos) + ", " + str(self.steps) + ")"
        return movStr
class Minimax:
    def __init__(self): #Initiates class
        pass
    def MiniMax(self, board=None, depth=0, bestMove=None, bestScore=None): #Returns highest scoring movement and its score
        if not board:
            board = Board()
        if not bestMove:
            bestMove = Movement([0, 0])
        if depth == 0: #If recursion over
            return [bestMove, 0] #Return best movement, score
        if depth > 0: #If recursion going
            movesTable = board.GetMovesTable() #Obtain movesTable
            bestMoves = []
            for i, j in [(x, y) for x in range(0, 6) for y in range(0, 6)]: #For each tile
                if movesTable[i][j] == []: #If no moves, continue
                    continue
                for movement in movesTable[i][j]: #For each movement
                    score = self.AssignScore(movement, board) #Assign score
                    boardClone = Board(board.turn) #Clone board
                    boardClone.board = board.CreateClone()
                    boardClone.MoveTile(movement) #Make movement in clone board
                    boardClone.ChangeTurn() #Change clone board's turn
                    score += self.MiniMax(boardClone, depth - 1)[1] #Iterates for next turn and adds to score
                    if board.turn == 1: #If player ID 1
                        if bestScore == None or score > bestScore: #Maximize score
                            bestScore = score
                            bestMoves = [movement]
                        elif score == bestScore:
                            bestMoves.append(movement) 
                    else:
                        if bestScore == None or score < bestScore: #Minimize score
                            bestScore = score
                            bestMoves = [movement]
                        elif score == bestScore:
                            bestMoves.append(movement)
                if bestMoves: #If more than one movement, return one at "random"
                    bestMove = bestMoves[random.randint(0, len(bestMoves) - 1)]
            if bestScore == None:
                bestScore = 0
            return [bestMove, bestScore]
    def AssignScore(self, movement=Movement([0, 0]), board=Board()): #Returns score for current path
        score = 0
        iPos = movement.iPos
        for i in range(len(movement.steps)): #For step in movement
            step = movement.steps[i]
            if abs(board.GetTileAtPos(movement.iPos)) != 2:  #If not king
                if step[0] == 0 or step[0] == 5: #Add conversion score
                    score += board.turn * 10
                score += board.turn * 10 #Add movement score
            if i == 0:
                direction = [step[0] - iPos[0], step[1] - iPos[1]] #Obtain step direction
            else:
                direction = [step[0] - movement.steps[i - 1][0], step[1] - movement.steps[i - 1][1]]
            if  not (-1 <= direction[0] <=1): #if tile jumped
                i = 1 if direction[0] > 0 else -1 if direction[0] < 0 else 0
                j = 1 if direction[1] > 0 else -1 if direction[1] < 0 else 0
                direction = [i, j]
                pos = [iPos[0] + direction[0], iPos[1] + direction[1]] #Get jumped tile position
                if board.InsideBounds(pos):
                    if abs(board.GetTileAtPos(pos)) == 2: #If jumped king
                        score += board.turn * 50 #Add kill score
                    score += board.turn * 50 #Add kill score
        return score
