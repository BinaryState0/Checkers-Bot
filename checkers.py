import copy 

#Codes for console output
red = "\033[31m"
blue = "\033[34m"
white = "\033[37m"

#TODO: Minimax algorithm implementation

class Board:
    def __init__(self): #Initiates board
        self.board = [[0 for _ in range(6)] for _ in range(6)] # 6x6 Array of 0s
        self.turn = 0
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
        for i in range(6):
            for j in range (6):
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
            for step in movement.steps: #For each step
                if  (
                        step[0] == 0 or 
                        step[0] == 5  
                    ): #Check for king
                        self.SetTileAtPos(iPos, self.turn * 2)
                self.SetTileAtPos(step, self.turn) #Move piece
                self.SetTileAtPos(iPos, 0) #Remove old piece
                direction = [step[0] - iPos[0], step[1] - iPos[1]]
                if  (
                        not (-1 <= direction[0] <=1)
                    ): #Piece jumped
                    i = direction[0] / direction[0]
                    j = direction[1] / direction[1] 
                    direction = [i, j]#Normalize direction vectors
                    pos = [iPos + direction]
                    self.SetTileAtPos(pos, 0)#Remove jumped pieces
    def GetMovesTable(self): #Returns a 6x6 table of arrays with possible movements for each piece in the turn
        moveSet = [[[] for _ in range(6)] for _ in range(6)] #Empty 6 x 6 table of arrays
        for i in range(6): #For each piece on the board
            for j in range(6):
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
                    self.GetTileAtPos(pos2) == self.turn
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
        for i in range(6): #For each tile
            for j in range(6):
                mov = self.board[i][j] - prevState.board[i][j] #Substract states
                if mov != 0:
                    mov = mov / abs(mov) #Normalizes to 1, 0 or -1
                movements[i][j] = mov
        return movements
    def ExtractMovement(self, prevState): #Returns movement between two boards, False if invalid
        movements = self.ExtractMovementsRaw(prevState)
        iPos = []
        tPos = []
        for i in range(6): #For each tile
            for j in range(6):
                pos = movements[i][j]
                pos *= self.turn #Player ID -1 (red) is inverted, this fixes it
                if pos == -1 and not iPos: #If state is -1, movement starts here
                    if not iPos: #Checks that it hasnt found another
                        iPos = [i, j]
                    else:
                        return False
        for i in range(6): #For each tile
            for j in range(6):
                pos = movements[i][j]
                pos *= self.turn
                if pos == 1 and not tPos: #If state is -1, movement starts here
                    if not tPos: #Checks that it hasnt found another
                        tPos = [i, j]
                    else:
                        return False
        movement = Movement(iPos, [tPos]) #Saves the movement
        return movement
    def ValidateMovement(self, movement): #Checks a movement against possible moves
        i, j = movement.iPos[0], movement.iPos[1]
        moves = self.GetMovesTable()[i][j]
        #print(movement)
        #print(red + str(moves) + white)
        for move in moves:
            #print(blue + str(move) + white)
            if move == movement:
                return True
        return False
    def CreateClone(self): #Returns an unlinked copy of the board
        boardCopy = copy.deepcopy(self.board)
        return boardCopy
class Minimax: #TODO
    def __init__(self, turn): #Initiates AI with player code turn
        self.turn = turn
class Movement:
    def __init__(self, iPos, steps = None): #Initiates with coordinates i, j
        self.iPos = iPos
        self.steps = steps
        if not steps:
            self.steps = []
    def __eq__(self, other):
        if self.iPos == other.iPos and self.steps == other.steps:
            return True
        return False
    def __repr__(self):
        movStr = "mov(" + str(self.iPos) + ", " + str(self.steps) + ")"
        return movStr
    def AddStep(self, k, h): #Adds a step to coords k, h
        self.steps.append([k, h])
    def Step(self):
        self.iPos = [self.steps.pop(0)]


