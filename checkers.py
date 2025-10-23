from __future__ import annotations
import copy 
import random

# Color codes for console output
red = "\033[31m"
blue = "\033[34m"
white = "\033[37m"
yellow = "\033[33m"
green = "\033[32m"

class Movement:
    """Provides functionality to easily store and compare board movements"""
    def __init__(self, iPos: list[int], steps = None, debug = False):
        """Initializes class with a starting position

        Args:
            iPos (list[int]): Starting position for the movement
            steps (List[List[int]], optional): List of board coordinates, in order. Defaults to None.
        """
        self.iPos = iPos
        self.steps = [] if steps is None else steps
        if debug: print(green + f"Created movement {repr(self)} with iPos {iPos} and steps {steps}" + white)
    def AddStep(self, pos: list[int], debug = False):
        """Adds a step

        Args:
            pos (list[int]): Position of the step to be added
        """
        self.steps.append(pos)
        if debug: print(green + f"Added step at position {pos} for movement {repr(self)}" + white)
    def Step(self, debug = False):
        """Removes the first step in the movement and saves it as the new initial position"""
        self.iPos = [self.steps.pop(0)]
        if debug: print(green + f"Advanced one step for movement {repr(self)}" + white)
    def Inverse(self, debug = False) -> Movement:
        """Returns a copy of the current movement, in reverse

        Returns:
            Movement: Inverse movement
        """
        stepsCount = len(self.steps)
        inverse = Movement([-1, -1])
        for step in range(stepsCount):
            step = stepsCount - step
            if step == stepsCount:
                inverse.iPos = self.steps[step]
            else:
                inverse.AddStep(self.steps[step])
        inverse.AddStep(self.iPos)
        if debug: print(green + f"Found inverse {inverse} for movement {repr(self)}" + white)
        return inverse
    def __eq__(self, other: Movement) -> bool:
        """Provides functionality to compare movements

        Args:
            other (Movement): Movement to compare against

        Returns:
            bool:
        """
        if  not isinstance(other, Movement):
            assert False, red + f"Cannot compare {type(other).__name__} with Movement" + white
        return self.iPos == other.iPos and self.steps == other.steps
    def __str__(self):
        movStr = "mov(" + str(self.iPos) + ", " + str(self.steps) + ")"
        return movStr
class Board:
    """Provides functionality to create a fully functioning 6x6 board of checkers"""
    def __init__(self, turn = 1, size = 6, difficulty = 3, debug = False):
        """
        Initializes the board class, creating a (size, size + 2) array of 0s, size must be an even number
        Args:
            turn (int, optional): Turn in which the board is started. Defaults to 1.
            size (int, optional): Size of the game's board, even numbers. Defaults to 6
            difficulty (int, optional): Difficulty of the game, affects default values of certain behaviours, between 1 and 5. Defaults to 3
        """
        self.board = [[0 for _ in range(size + 2)] for _ in range(size)]
        assert turn in range(-1, 2),  red + f"Attempted to create board {repr(self)} invalid turn ID" + white
        self.turn = turn
        assert size % 2 == 0, red + f"Attempted to create board {repr(self)} invalid size" + white
        self.size = size
        assert difficulty in range(1, 6), red + f"Attempted to create board {repr(self)} invalid difficulty" + white
        self.difficulty = difficulty
        self.turnCount = 1
        self.staleTurns = 0
        if debug: print(green + f"Creating board {repr(self)} at turn [{turn}] with size [{size}] at difficulty [{difficulty}]" + white)
    def __str__(self) -> str:
        """Returns the board as a string, for use in console prints
        
        Returns:
            str: String representation of the board
        """
        boardStr = f"Turn: {self.turnCount} | To stalemate: {40 - self.staleTurns} | "
        if self.turn == 1:
            boardStr += blue + "Blue moves" + white + "\n"
        else:
            boardStr += red + "Red moves" + white + "\n"
        boardStr += yellow
        for i in range(self.size + 4):
            if i == 0 or i == self.size + 3:
                boardStr += "x "
            elif i == 1 or i == self.size + 2:
                boardStr += "| "
            else:
                boardStr += f"{i - 1} "
        boardStr += "\n" + white
        for i in range(self.size):
            boardStr += yellow + f"{i + 1} " + white
            for j in range(self.size + 4):
                if j == 1 or j == self.size + 2:
                    boardStr += yellow + "| " + white
                else:
                    pos = [i, j - 1]
                    if not self.InsideBounds(pos):
                        continue
                    tile = self.GetTileAtPos(pos)
                    if tile == 0:
                        boardStr += "· "
                    elif tile > 0:
                        boardStr += blue
                        if tile == 1:
                            boardStr += "o "
                        else:
                            boardStr += "O "
                        boardStr += white
                    else:
                        boardStr += red
                        if tile == -1:
                            boardStr += "ø "
                        else:
                            boardStr += "Ø "
                        boardStr += white
            boardStr += yellow + f"{i + 1} " + white
            boardStr += "\n"
        boardStr += yellow
        for i in range(self.size + 4):
            if i == 0 or i == self.size + 3:
                boardStr += "x "
            elif i == 1 or i == self.size + 2:
                boardStr += "| "
            else:
                boardStr += f"{i - 1} "
        boardStr += "\n" + white
        return boardStr
    def SetBoard(self, debug = False):
        """Resets the board to an initial state, with 6 pieces per player arranged in a regular pattern"""
        self.turnCount = 1
        self.turn = 1
        self.staleTurns = 0
        if debug: print(green + f"Resetting board {repr(self)} with size {self.size}" + white)
        # Reset playable area
        for i, j in [(x, y) for x in range(0, self.size) for y in range(0, self.size)]:
            pos = [i, j + 1]
            # Checks for a checkerboard pattern in first and last two rows to set pieces, resets others to 0
            if j % 2 == ((i +  1) % 2): 
                if i < 2:
                    self.SetTileAtPos(pos, -1, debug)
                elif i > self.size - 3:
                    self.SetTileAtPos(pos, 1, debug)
                else: self.SetTileAtPos(pos, 0, debug)
            else: 
                self.SetTileAtPos(pos, 0, debug)
        # Reset cemetery
        for i, j in [(x, y) for x in range(0, self.size) for y in [0, self.size  + 1]]:
            pos = [i, j]
            self.SetTileAtPos(pos, 0)
    def GetTileAtPos(self, pos: list[int], debug = False) -> int:
        """
        Returns the tile ID at a given position
        Args:
            pos (list[int]): Position [x, y] to check 

        Returns:
            int: ID of the piece at given position
        """
        assert self.InsideBounds(pos, False), red + f"Could not read position {pos} because it is not inside the board" + white
        ID = self.board[pos[0]][pos[1]]
        if debug: print(green + f"Found tile with id [{ID}] at position {pos} for board {repr(self)}" + white)
        return ID
    def SetTileAtPos(self, pos: list[int], ID: int, debug = False):
        """Changes the tile ID at a given position
        
        Args:
            pos (list[int]): Position [x, y] to change
            type (int): ID the position will be set to
        """
        assert self.InsideBounds(pos, False), red + f"Could not write to position {pos} because it is not inside the board" + white
        if debug: print(green + f"Replaced tile at position {pos} with id [{ID}] for board {repr(self)}" + white)
        self.board[pos[0]][pos[1]] = ID
    def GetAmmountOf(self, ID: int, game = True, debug = False) -> int:
        """Returns the ammount of tiles with a certain ID left in the playable area

        Args:
            ID (int): ID to search tiles of
            game (bool): If false, will count in cemetery area

        Returns:
            int: Ammount of tiles with given ID
        """
        assert ID in range(-2, 3), red + f"Could not count ammount of tiles with id {ID} as it is not a valid ID" + white
        board = [[0 for _ in range(self.size + 2)] for _ in range(self.size)]
        count = 0
        if game: 
            for i, j in [(x, y) for x in range(0, self.size) for y in range(0, self.size)]:
                j += 1
                board[i][j] = self.board[i][j]
        else:
            for i, j in [(x, y) for x in range(0, self.size) for y in range(0, [0, self.size + 2])]:
                board[i][j] = self.board[i][j]
        for i in board:
            count += i.count(ID)
        if debug: print(green + f"Found a total of {count} tiles with id [{ID}] for board {repr(self)}" + white)
        return count
    def InsideBounds(self, pos: list[int], game = True, debug = False) -> bool:
        """Checks if a given position is inside the board

        Args:
            pos (list[int]): Position to check
            game (bool): If false will also check cemetery area

        Returns:
            bool:
        """
        width = [1 if game else 0, self.size if game else self.size + 1]
        if (0 <= pos[0] <= (self.size - 1)) and (width[0] <= pos[1] <= width[1]):
            if debug: print(green + f"Position {pos} is inside of board {repr(self)}" + white)
            return True
        else:
            if debug: print(green + f"Position {pos} is outside of board {repr(self)}" + white)
            return False
    def MoveTile(self, movement: Movement, validate = True, death = False, debug = False):
        """Validates and performs a given movement, if necessary will move tiles to cemetery or promote to kings

        Args:
            movement (Movement): Movement to perform
            validate (bool, optional): If movement should be validated. Defaults to True.
            death (bool, optional): If the piece is being moved to the cemetery. Defaults to False.

        Returns:
            False: If movement is invalid
        """
        if debug: print(green + f"Performing movement {movement} for board {repr(self)}" + white)
        iPos = movement.iPos
        prevStep = [-1, -1]
        if self.ValidateMovement(movement, debug) or not validate:
            for step in movement.steps:
                if prevStep == [-1, -1]:
                    prevStep = iPos
                # Perform movement
                i, j, k, l = prevStep[0], prevStep[1], step[0], step[1]
                prevStep = step
                self.board[i][j], self.board[k][l] = self.board[k][l], self.board[i][j]
                if debug: print(green + f"Swapped pieces at positions {[i, j]}, {[k, l]} for board {repr(self)}" + white)
                # Check for killed tiles
                direction = [k - i, l - j]
                if abs(direction[0]) > 1 and abs(direction[1]) > 1 and not death:
                    k = 1 if direction[0] > 0 else -1 if direction[0] < 0 else 0
                    l = 1 if direction[1] > 0 else -1 if direction[1] < 0 else 0
                    pos = [i + k, j + l]
                    if self.InsideBounds(pos, death):
                        cPos = [-1, -1]
                        if self.turn == 1:
                            j = self.size - 1
                            for i in range(self.size):
                                if self.GetTileAtPos([i, j]) == 0:
                                    cPos = [i, j]
                                    continue
                        else:
                            j = 0
                            for i in range(self.size):
                                i = self.size - 1 - i
                                if self.GetTileAtPos([i, j]) == 0:
                                    cPos = [i, j]
                                    continue
                        move = Movement(pos, [cPos])
                        # Move tile to unoccupied cemetery slot
                        if debug: print(green + f"Moved tile at position {pos} to cemetery position {cPos} for board {repr(self)}" + white)
                        self.MoveTile(move, False, True)
                        self.staleTurns = -1
                    else:
                        return False
            # Convert to king
            if  (
                    ((prevStep[0] == 0 or prevStep[0] == self.size - 1) and
                    abs(self.GetTileAtPos(step)) != 2) and
                    not death
                ):
                    self.SetTileAtPos(prevStep, self.turn * 2)
                    self.staleTurns = -1
                    if debug: print(green + f"Promoted tile at position {prevStep} for board {repr(self)}" + white)
        else:
            return False
    def BuildMovementsTable(self, debug = False) -> list[list[list[Movement]]]:
        """Returns an array of lists with possible movements for the current board

        Returns:
            list[list[list[Movement]]]: Array of lists with possible movements
        """
        if debug: print(green + f"Building movements table for board {repr(self)}" + white)
        moveSet = [[[] for _ in range(self.size + 2)] for _ in range(self.size)]
        for i, j in [(x, y) for x in range(0, self.size) for y in range(0, self.size)]:
            iPos = [i, j + 1]
            if (self.GetTileAtPos(iPos) == self.turn or self.GetTileAtPos(iPos) == 2 * self.turn):
                paths = self.ExtractMovements(iPos, debug = debug)
                for path in paths:
                    if path != []:
                        movement = Movement(iPos, path)
                        moveSet[i][j + 1].append(movement)
        return moveSet
    def ExtractMovements(self, pos: list[int], iPos = None,  path = None, paths = None, visited = None, debug = False) -> list[list[list[int]]]:
        """Searches recursively for every possible movement in a certain tile

        Args:
            pos (list[int]): Current position to search
            iPos (int, optional): Initial search position. Defaults to None.
            path (list[list[int]], optional): Current path being recorded. Defaults to None.
            paths (list[list[list[int]]], optional): List of paths recorded. Defaults to None.
            visited (list[list[int]], optional): List of visited tiles. Defaults to None.

        Returns:
            list[list[list[int]]]: List of all possible paths for the tile
        """ 
        assert self.InsideBounds(pos, False), red + f"Could not extract movements at {pos} because it is not inside the board" + white
        # Initializes variables
        if not iPos:
            iPos = pos
        if not path:
            path = []
        if not paths:
            paths = []
        if not visited:
            visited = []
        # Check every diagonal direction
        for i, j in [(x, y) for x in [-1, 1] for y in [-1, 1]]:
            if debug: print(green + f"Searching movements at position {pos} in direction {[i, j]} for board {repr(self)}" + white)
            pos2 = [pos[0] + i, pos[1] + j]
            #Checks if movement to tile would be valid, backtracks and saves positions accordingly
            if  (
                    not self.InsideBounds(pos2) or
                    pos2 in visited
                ):
                if (path and path not in paths):
                    paths.append(path.copy())
                continue
            if  ( 
                    (abs(self.GetTileAtPos(iPos)) != 2 and i == self.turn) or
                    self.GetTileAtPos(pos2) == self.turn or
                    self.GetTileAtPos(pos2) == self.turn * 2
                ):
                if  (path and path not in paths):
                    visited.append(pos2)
                    paths.append(path.copy())
                    path.pop()
                continue
            if (self.GetTileAtPos(pos2) == 0):
                if (path == []):
                    path.append(pos2)
                    visited.append(pos2)
                    paths.append(path.copy())
                    path.pop()
                continue
            # Continues on the next tile after
            else:
                #Checks if movement to tile would be valid, backtracks and saves positions accordingly
                pos3 = [pos2[0] + i, pos2[1] + j]
                if  (not self.InsideBounds(pos3)):
                    
                    if (path and path not in paths):
                        paths.append(path.copy())
                        visited.append(pos2)
                    continue
                if self.GetTileAtPos(pos3) != 0:
                    if (path and path not in paths):
                        paths.append(path.copy())
                        visited.append(pos2)
                    continue
                path.append(pos3)
                # Recursion
                if (path and path not in paths):
                    paths.append(path.copy())
                    visited.append(pos2)
                    paths = self.ExtractMovements(pos3, iPos, path, paths, visited)
                    path.pop()
        if debug: print(green + f"Found movements {paths} at position {iPos} for board {repr(self)}" + white)
        return paths
    def ExtractChangeValues(self, other: Board, debug = False) -> list[list[int]]:
        """Analizes the changes between two boards and returns it as an array of values

        Args:
            other (Board): Board to be compared against

        Returns:
            list[list[int]]: Array containing values of 1 or -1 to indicate movement
        """
        assert self.size == other.size, red + "Could not find change values between different sized boards" + white
        if debug: print(green + f"Extracting change values for board {repr(self)}" + white)
        values = [[[] for _ in range(self.size + 2)] for _ in range(self.size)]
        for i, j in [(x, y) for x in range(0, self.size) for y in range(0, self.size + 2)]:
            value = self.board[i][j] - other.board[i][j]
            if value != 0:
                value = value / abs(value)
            values[i][j] = value
        return values
    def FindMovement(self, other: Board, debug = False) -> Movement: # Returns movement between two boards, False if invalid #TODO: TESTING
        """Analizes two boards and returns a movement between them if it exists, else returns False

        Args:
            other (Board): Board to be compared against

        Returns:
            Movement: Movement that happened between boards, False if not found
        """
        assert self.size == other.size, red + "Could not find movement between different sized boards" + white
        changeValues = self.ExtractChangeValues(other, debug)
        movesTable = self.BuildMovementsTable(debug)
        boardClone = Board(self.turn, board.size)
        for i, j in [(x, y) for x in range(0, self.size) for y in range(0, self.size + 2)]:
            for movement in movesTable[i][j]:
                boardClone.board = self.CreateClone(debug)
                boardClone.MoveTile(movement, debug)
                cloneValues = self.ExtractChangeValues(boardClone, debug)
                if changeValues == cloneValues:
                    if debug: print(green + f"Found movement {movement} between boards {repr(self)} and {repr(other)}" + white)
                    return movement
        if debug: print(green + f"No movement found between boards {repr(self)} and {repr(other)}" + white)
        return False
    def ValidateMovement(self, movement: Movement, debug = False) -> bool:
        """Checks if a given movement is valid against all currently possible movements

        Args:
            movement (Movement): Movement to be validated

        Returns:
            bool:
        """
        paths = self.ExtractMovements(movement.iPos, debug=debug) #Get movesTable
        for path in paths: #For each move
            move = Movement(movement.iPos, path)
            if move == movement: #If movement == inside movesTable
                if debug: print(green + f"Validated movement {movement} for board {repr(self)}" + white)
                return True #True
        if debug: print(green + f"Could not validate movement {movement} for board {repr(self)}" + white)
        return False
    def CreateClone(self, debug = False) -> list[list[int]]:
        """Uses the deepcopy library to easily create a copy of the current board

        Returns:
            list[list[int]]: board value of the current Board
        """
        if debug: print(green + f"Created deep copy of board {repr(self)}" + white)
        boardCopy = copy.deepcopy(self.board)
        return boardCopy
    def ChangeTurn(self, debug = False):
        """Changes the current turn of the board and sums one to the turnCount"""
        self.staleTurns += 1
        self.turnCount += 1
        if self.turn == 0:
            self.turn = 1
        else:
            self.turn *= -1
        if debug: print(green + f"Advanced to turn [{self.turnCount}] for player ID [{self.turn}] at board {repr(self)}" + white)
    def PossibleMovements(self, pos: list[int], debug = False) -> tuple[str, list[Movement]]:
        """Returns a string detailing possible movements for a tile, to use in consoles. Also returns the list.

        Args:
            pos (list[int]): Position of the tile to search in. Defaults to [-1, -1].

        Returns:
            tuple[str, list[Movement]]: Tuple containing the string and list form of possible movements
        """
        assert self.InsideBounds(pos, False), red + f"Could not find movements at position {pos} because it is not inside the board" + white
        i, j = pos[0], pos[1]
        pos[0] += 1
        movesStr = ""
        movements = self.BuildMovementsTable(debug)
        movesStr += f"Movements available for tile {pos}:\n"
        for x in range(len(movements[i][j])):
            movesStr += f"{x + 1}: From {pos}"
            for step in movements[i][j][x].steps:
                step[0] += 1
                movesStr += f" to {step}"
                step[0] -= 1
            movesStr += "\n"
        if debug: print(green + f"Found movements {movements[i][j]} for board {repr(self)}" + white)
        return movesStr, movements[i][j]
    def IsStalemate(self, condition = 40, debug = False) -> bool: # ? 40 seems like a lot but it is tournament rules
        """Checks for stalemate conditions, returns True if game ended on stalemate

        Args:
            condition (int): Ammount of stale turns after which a stalemate is declared. Defaults to 10

        Returns:
            bool: Returns True if there is no possible movements or staleTurns is over condition
        """
        if debug: print(green + f"Checking for stalemate at turn [{self.turn}] with [{self.staleTurns}] stale turns for board {repr(self)}" + white)
        if self.staleTurns > condition or AI.MiniMax(self, 1, debug=debug)[0] == Movement([-1, -1]):
            return True
        return False
    def IsCheckmate(self, debug = False) -> bool:
        """Checks if there is any tiles remaining for the current player

        Returns:
            bool: True if tiles ammount is greater than 0
        """
        if debug: print(green + f"Checking for checkmate at turn [{self.turn}] for board {repr(self)}" + white)
        tiles = 0
        for i in [self.turn, self.turn * 2]:
            tiles += self.GetAmmountOf(i)
        if tiles == 0:
            return True
        return False
class AI:
    """Provides functionality for the checkers AI"""
    def MiniMax(board: Board, depth = None, bestMove = None, bestScore = None, mults = [10, 20], debug = False) -> tuple[Movement, int]:
        """Searches for the optimal movement(s) in a board and returns it (Random if multiple) along with it's assigned score

        Args:
            board (Board): Board to evaluate.
            depth (int): Depth of search, low values are recommended. Defaults to board's difficulty value.
            bestMove (Movement, optional): Highest scoring move found. Defaults to None.
            bestScore (int, optional): Highest scoring move's score value. Defaults to None.
            mults (list[int]): List of multipliers for score addition [movement, killing]. Defaults to [10, 20]

        Returns:
            tuple[Movement, int]: Tuple containing the optimal movement and it's associated score
        """
        if debug: print(green + f"Initiating minimax algorithm for board {repr(board)} at depth [{depth}]" + white)
        # Initializes variables
        if depth is None:
            depth = board.difficulty
        if bestMove is None:
            bestMove = Movement([-1, -1])
        # Last depth level, returns values found
        if depth == 0:
            return [bestMove, 0]
        # Algorithm
        if depth > 0:
            movesTable = board.BuildMovementsTable(debug)
            bestMoves = []
            # Check all movements of every tile that can move on the board
            for i, j in [(x, y) for x in range(0, board.size) for y in range(0, board.size)]:
                j += 1
                if movesTable[i][j] == []:
                    continue
                for movement in movesTable[i][j]:
                    # Adds score and iterates
                    score = AI.AssignScore(movement, board, mults, debug)
                    boardClone = Board(board.turn, board.size)
                    boardClone.board = board.CreateClone(debug)
                    boardClone.MoveTile(movement, debug=debug)
                    boardClone.ChangeTurn(debug)
                    score += AI.MiniMax(boardClone, depth - 1, debug=debug)[1]
                    # Maximize for ID 1, minimize for ID -1
                    if board.turn == 1:
                        if bestScore == None or score > bestScore:
                            bestScore = score
                            bestMoves = [movement]
                        elif score == bestScore:
                            bestMoves.append(movement) 
                    else:
                        if bestScore == None or score < bestScore:
                            bestScore = score
                            bestMoves = [movement]
                        elif score == bestScore:
                            bestMoves.append(movement)
                # Chooses a random movement from the list of highest scoring movements
                if bestMoves:
                    bestMove = bestMoves[random.randint(0, len(bestMoves) - 1)]
            if bestScore == None:
                bestScore = 0
            if debug: print(green + f"Minimax has found movement {bestMove} with score [{bestScore}] for board {repr(board)}" + white)
            return bestMove, bestScore
    def AssignScore(movement: Movement, board: Board, mults = [10, 20], debug = False) -> int:
        """Returns the total score sum for a given movement, uses hard coded values

        Args:
            movement (Movement): Movement to be appraised
            board (Board): Board where the movement is performed
            mults (list[int]): List of multipliers for score addition [movement, killing]. Defaults to [10, 20]

        Returns:
            int: Score calculated
        """
        score = 0
        prevStep = [-1, -1]
        # Through every step in the movement
        for i in range(len(movement.steps)):
            step = movement.steps[i]
            if prevStep == [-1, -1]:
                prevStep == movement.iPos
            # Add movement score, doubled if converting
            if abs(board.GetTileAtPos(movement.iPos)) != 2:
                if step[0] == 0 or step[0] == 5:
                    score += board.turn * mults[0]
                score += board.turn * mults[0]
            direction = [step[0] - prevStep[0], step[1] - prevStep[1]]
            # Add killing score, doubled if king
            if  not (-1 <= direction[0] <=1):
                i = 1 if direction[0] > 0 else -1 if direction[0] < 0 else 0
                j = 1 if direction[1] > 0 else -1 if direction[1] < 0 else 0
                direction = [i, j]
                pos = [prevStep[0] + direction[0], prevStep[1] + direction[1]]
                if board.InsideBounds(pos):
                    if abs(board.GetTileAtPos(pos)) == 2:
                        score += board.turn * mults[1]
                    score += board.turn * mults[1]
        if debug: print(green + f"Assigned score of [{score}] to movement {movement} for board {repr(board)}" + white)
        return score

board = Board(1, 8)
board.InsideBounds([6, 2], game = False, debug = True)