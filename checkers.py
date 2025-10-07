import copy 
import random

#Codes for console output
red = "\033[31m"
blue = "\033[34m"
white = "\033[37m"

#TODO: Minimax algorithm implementation

class Board:
    def __init__(self, turn = 1): #Initiates board
        self.board = [[0 for _ in range(6)] for _ in range(6)] # 6x6 Array of 0s
        self.turn = turn
    def __str__(self): #Converts board to a string
        boardStr = "GameBoard:\n"
        for i in range(6):
            for j in range(6):
                pos = [i, j]
                tile = self.GetTileAtPos(pos)
                if tile == 0:
                    boardStr += white + "·" #Empty
                elif tile == -1: 
                    boardStr += red + "ø"	#Player 1, top
                elif tile == 1:
                    boardStr += blue + "o" #Player 2, bottom
                elif tile == -2:
                    boardStr += red + "Ø" #Player 1 king
                elif tile == 2:
                    boardStr += blue + "O" #Player 2 king
                boardStr += " "
            boardStr += "\n"
        boardStr += "\033[37m"
        return boardStr
    def SetBoard(self): #Resets board
        for i, j in [(x, y) for x in range(0, 6) for y in range(0, 6)]:
            pos = [i, j]
            if j % 2 == ((i +  1) % 2): #Checks to see if a man should be there
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
    def MoveTile(self, movement): #Swaps tile i1,j1 and i2,j2, kills and converts. If movement is invalid returns FALSE
        iPos = movement.iPos
        if self.ValidateMovement(movement):#Validate movement
            for x in range(len(movement.steps)): #For each step
                step = movement.steps[x]
                prevStep = movement.steps[x-1]
                if  (
                        (step[0] == 0 or 
                        step[0] == 5) and
                        abs(self.GetTileAtPos(step)) != 2
                    ): #Check for king
                        self.SetTileAtPos(iPos, self.turn * 2)
                if x == 0: #Swap tiles
                    self.board[iPos[0]][iPos[1]], self.board[step[0]][step[1]] = self.board[step[0]][step[1]], self.board[iPos[0]][iPos[1]]
                    direction = [step[0] - iPos[0], step[1] - iPos[1]]
                else:
                    self.board[prevStep[0]][prevStep[1]], self.board[step[0]][step[1]] = self.board[step[0]][step[1]], self.board[prevStep[0]][prevStep[1]]
                    direction = [step[0] - prevStep[0], step[1] - prevStep[1]]
                if  not (-1 <= direction[0] <=1): #Piece jumped
                    i = 1 if direction[0] > 0 else -1 if direction[0] < 0 else 0
                    j = 1 if direction[1] > 0 else -1 if direction[1] < 0 else 0
                    direction = [i, j]
                    pos = [iPos[0] + direction[0], iPos[1] + direction[1]] #Get jumped tile position
                    if 0 <= pos[0] < 6 and 0 <= pos[1] < 6:
                        self.SetTileAtPos(pos, 0) #Remove jumped tile
                    else:
                        return False
        else:
            return False
    def GetMovesTable(self): #Returns a 6x6 table of arrays with possible movements for each piece in the turn
        moveSet = [[[] for _ in range(6)] for _ in range(6)] #Empty 6 x 6 table of arrays
        for i, j in [(x, y) for x in range(0, 6) for y in range(0, 6)]: #For each piece on the board
            iPos = [i, j] #Initial position
            if (self.GetTileAtPos(iPos) == self.turn or self.GetTileAtPos(iPos) == 2 * self.turn): #Checks for current turn
                paths = self.CheckMovement(iPos) #Saves posible paths
                for path in paths: #For each path
                    if path != []: #If not empty
                        movement = Movement(iPos, path) #Saves path as movement
                        moveSet[i][j].append(movement) #Saves movement to array
        return moveSet
    def CheckMovement(self, pos, iPos = None,  path = None, paths = None, visited = None): #Returns an array of possible steps
        if not iPos: #Initialization of lists to avoid duplication of values
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
                    not(0 <= pos2[0] <= 5 and
                    0 <= pos2[1] <= 5) or
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
                    not( 0 <= pos3[0] <= 5 and
                    0 <= pos3[1] <= 5)
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
        movements = [[[] for _ in range(6)] for _ in range(6)] #6x6 board for value storage
        for i, j in [(x, y) for x in range(0, 6) for y in range(0, 6)]: #For each tile
            mov = self.board[i][j] - prevState.board[i][j] #Substract states
            if mov != 0:
                mov = mov / abs(mov) #Normalizes to 1, 0 or -1
            movements[i][j] = mov
        return movements
    def ExtractMovement(self, prevState): #Returns movement between two boards, False if invalid
        movements = self.ExtractMovementsRaw(prevState)
        iPos = []
        tPos = []
        for i, j in [(x, y) for x in range(0, 6) for y in range(0, 6)]: #For each tile
            pos = movements[i][j]
            pos *= self.turn #Player ID -1 (red) is inverted, this fixes it
            if pos == -1 and not iPos: #If state is -1, movement starts here
                if not iPos: #Checks that it hasnt found another
                    iPos = [i, j]
                else:
                    return False
        for i, j in [(x, y) for x in range(0, 6) for y in range(0, 6)]: #For each tile
            pos = movements[i][j]
            pos *= self.turn
            if pos == 1 and not tPos: #If state is -1, movement starts here
                if not tPos: #Checks that it hasnt found another
                    tPos = [i, j]
                else:
                    return False
        movement = Movement(iPos, [tPos]) #Saves the movement
        return movement
    def ValidateMovement(self, movement): #Checks a movement against possible moves and returns True or False
        i, j = movement.iPos[0], movement.iPos[1]
        moves = self.GetMovesTable()[i][j] #Get movesTable
        for move in moves: #For each move
            if move == movement: #If movement is inside movesTable
                return True #True
        return False
    def CreateClone(self): #Returns an unlinked copy of the board
        boardCopy = copy.deepcopy(self.board)
        return boardCopy
    def ChangeTurn(self): #Changes the current turn of the current board
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
        if self.iPos == other.iPos and self.steps == other.steps:
            return True
        return False
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
            bestScore = 0
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
                    print(score)
                    if board.turn == 1: #If player ID 1
                        if bestScore is None or score > bestScore: #Maximize score
                            bestScore = score
                            bestMoves = [movement]
                        elif score == bestScore:
                            bestMoves.append(bestMove) 
                    else:
                        if bestScore is None or score < bestScore: #Minimize score
                            bestScore = score
                            bestMoves = [movement]
                        elif score == bestScore:
                            bestMoves.append(movement)
                if bestMoves: #If more than one movement, return one at "random"
                    bestMove = bestMoves[random.randint(0, len(bestMoves) - 1)]
            if bestScore is None:
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
                if 0 <= pos[0] < 6 and 0 <= pos[1] < 6:
                    if abs(board.GetTileAtPos(pos)) == 2: #If jumped king
                        score += board.turn * 50 #Add kill score
                    score += board.turn * 50 #Add kill score
        return score

board = Board(-1)
board.SetBoard()
prevBoard = Board()
minimax = Minimax()
print(board)
def mainTest():
    if board.turn != 0:
        movesTable = board.GetMovesTable()
        anyMoves = any(movesTable[i][j] for i in range(6) for j in range(6))
        print("Any moves available for turn", board.turn, ":", anyMoves)
        movement = minimax.MiniMax(board, 3)[0]
        if movement == Movement([0, 0]):
            #TODO: fix this one, border checks may be cause
            print(f"Player {-1 * board.turn} wins by blockage")
            input()
            board.turn = 0
            mainTest()
        print(movement)
        board.MoveTile(movement)
        board.ChangeTurn()
        print(board)
        if board.GetAmmountOf(board.turn) == 0 and board.GetAmmountOf(board.turn * 2) == 0:
            print(f"Player {board.turn} wins")
            input()
            board.turn = 0
            mainTest()
        input()
        mainTest()
    else:
        board.SetBoard()
        board.turn = -1

mainTest()