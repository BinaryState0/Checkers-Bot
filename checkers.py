from __future__ import annotations
from constants import *
from copy import deepcopy
from random import randint

class Tile:
    """Abstract class to simplify Tile control"""
    def __init__(self, x: int = 0, y: int = 0, ID: int = 0):
        """Initializes the class

        Args:
            x (int, optional): X coordinate of the tile. Defaults to 0.
            y (int, optional): Y coordinate of the tile. Defaults to 0.
            ID (int, optional): ID of the tile. Defaults to 0.
        """
        assert isinstance(x, int) and isinstance(y, int), red + "Tile coordinates must be an integer" + white
        assert isinstance(ID, int), red + "Tile ID must be an integer" + white
        self.x, self.y, self.ID = x, y, ID
    def __repr__(self):
        return f"Tile([{self.x}, {self.y}], {self.ID})"  
    def __eq__(self, other):
        """Provides functionality to compare tiles

        Args:
            other (Tile): Tile to compare against

        Returns:
            bool:
        """
        if  not isinstance(other, Tile):
            assert False, red + f"Cannot compare {type(other).__name__} with Tile" + white
        return self.x == other.x and self.y == other.y and self.ID == other.ID
class TileMovement:
    """Provides functionality to easily store and compare board movements"""
    def __init__(self, steps: list[Tile], debug = False):
        """Initializes class with a starting position

        Args:
            steps (List[Tile]): List of board tiles with respective coordinates, in order.
        """
        assert len(steps) > 0, red + f"A movement must contain at least one step" + white
        for step in steps:
            assert isinstance(step, Tile), red + f"Steps must be of type {Tile}" + white
        self.steps = steps
        if debug: print(green + f"Created {TileMovement} with steps {steps}" + white)
    def AddStep(self, step: Tile, debug = False):
        """Adds a step

        Args:
            step (Tile): Step to be added.
        """
        assert isinstance(step, Tile), red + f"Steps must be of type {Tile}" + white
        self.steps.append(step)
        if debug: print(green + f"Added step {Tile} for movement {repr(self)}" + white)
    def Step(self, debug = False):
        """Removes the first step in the movement and saves it as the new initial position"""
        self.steps.pop(0)
        if debug: print(green + f"Advanced one step for movement {repr(self)}" + white)
    def __eq__(self, other: TileMovement) -> bool:
        """Provides functionality to compare movements

        Args:
            other (TileMovement): TileMovement to compare against

        Returns:
            bool:
        """
        if  not isinstance(other, TileMovement):
            assert False, red + f"Cannot compare {type(other).__name__} with TileMovement" + white
        return self.steps == other.steps
    def __str__(self):
        return f"TileMovement({str(self.steps)})"
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
        #Board creation
        assert size % 2 == 0 and size > 0, red + f"Attempted to create board {repr(self)} with invalid size" + white
        self.width, self.height = size + 2, size
        self.board = [[Tile() for _ in range(size + 2)] for _ in range(size)]
        for i, j in [(x, y) for x in range(0, self.height) for y in range(0, self.width)]:
            self.board[i][j].x, self.board[i][j].y = i, j
        #Board configuration
        assert turn in range(-1, 2),  red + f"Attempted to create board {repr(self)} with invalid turn ID" + white
        self.turn = turn
        assert difficulty in range(1, 6), red + f"Attempted to create board {repr(self)} with invalid difficulty" + white
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
        for i in range(self.height + 4):
            if i == 0:
                boardStr += "c | x "
            elif i == self.height + 3:
                boardStr += "x | c "
            elif i == 1 or i == self.height + 2:
                boardStr += "| "
            else:
                boardStr += f"{i - 1} "
        boardStr += "\n" + white
        for i in range(self.height):
            for j in range(self.width + 9):
                pos = [-1, -1]
                if j in [1, 3, self.width + 5, self.width + 3]:
                    boardStr += yellow + "| " + white
                elif j in [2, self.width + 4]:
                    boardStr += yellow + f"{i + 1} " + white
                elif j == 0:
                    pos = [i, 0]
                elif j in range(4, self.width + 2):
                    pos = [i, j - 3]
                elif j == self.width + 6:
                    pos = [i, self.width - 1]
                if not self.InsideBounds(pos, game = False):
                    continue
                tile = self.board[pos[0]][pos[1]].ID
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
            boardStr += "\n"
        boardStr += yellow
        for i in range(self.height + 4):
            if i == 0:
                boardStr += "c | x "
            elif i == self.height + 3:
                boardStr += "x | c "
            elif i == 1 or i == self.height + 2:
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
        if debug: print(green + f"Resetting board {repr(self)} with size {self.height}" + white)
        # Reset playable area
        for i, j in [(x, y) for x in range(0, self.height) for y in range(0, self.width - 2)]:
            pos = [i, j + 1]
            # Checks for a checkerboard pattern in first and last two rows to set pieces, resets others to 0
            if j % 2 == ((i +  1) % 2):
                if i < 2:
                    self.board[i][j + 1].ID = -1
                elif i > self.height - 3:
                    self.board[i][j + 1].ID = 1
                else: self.board[i][j + 1].ID = 0
            else: 
                self.board[i][j + 1].ID = 0
        # Reset cemetery
        for i, j in [(x, y) for x in range(0, self.height) for y in [0, self.width - 1]]:
            self.board[i][j].ID = 0
    def GetAmmountOf(self, ID: int, game = True, debug = False) -> int:
        """Returns the ammount of tiles with a certain ID left in the playable area

        Args:
            ID (int): ID to search tiles of
            game (bool): If false, will count in cemetery area

        Returns:
            int: Ammount of tiles with given ID
        """
        assert ID in range(-2, 3), red + f"Could not count ammount of tiles with id {ID} as it is not a valid ID" + white
        board = [[0 for _ in range(self.width)] for _ in range(self.height)]
        count = 0
        if game: 
            for i, j in [(x, y) for x in range(0, self.width - 2) for y in range(0, self.height)]:
                j += 1
                board[i][j] = self.board[i][j].ID
        else:
            for i, j in [(x, y) for x in range(0, self.height) for y in [0, self.width - 1]]:
                board[i][j] = self.board[i][j].ID
        for i in board:
            count += i.count(ID)
        if debug: print(green + f"Found a total of {count} tiles with id [{ID}] for board {repr(self)}" + white)
        return count
    def InsideBounds(self, pos: list[int], game = True, debug = False) -> bool:
        """Checks if a given position is inside the board

        Args:
            pos (list[int]): Position [x, y] to check
            game (bool): If false will also check cemetery area

        Returns:
            bool:
        """
        width = [1 if game else 0, self.width - 2 if game else self.width - 1]
        if (0 <= pos[0] <= (self.height - 1)) and (width[0] <= pos[1] <= width[1]):
            if debug: print(green + f"Position {pos} is inside of board {repr(self)}" + white)
            return True
        else:
            if debug: print(green + f"Position {pos} is outside of board {repr(self)}" + white)
            return False
    def MoveTile(self, movement: TileMovement, validate = True, death = False, debug = False):
        """Validates and performs a given movement, if necessary will move tiles to cemetery or promote to kings

        Args:
            movement (TileMovement): TileMovement to perform
            validate (bool, optional): If movement should be validated. Defaults to True.
            death (bool, optional): If the piece is being moved to the cemetery. Defaults to False.

        Returns:
            False: If movement is invalid
        """
        if debug: print(green + f"Performing movement {movement} for board {repr(self)}" + white)
        prevStep = Tile(-1, -1)
        if not validate or self.ValidateMovement(movement, debug):
            for step in movement.steps:
                if prevStep == Tile(-1, -1):
                    prevStep = step
                    continue
                # Perform movement
                i, j, k, l = prevStep.x, prevStep.y, step.x, step.y
                prevStep = step
                self.board[i][j], self.board[k][l] = self.board[k][l], self.board[i][j]
                if debug: print(green + f"Swapped tiles at positions {[i, j]}, {[k, l]} for board {repr(self)}" + white)
                # Check for killed tiles
                direction = [k - i, l - j]
                if abs(direction[0]) > 1 and abs(direction[1]) > 1 and not death:
                    k = 1 if direction[0] > 0 else -1 if direction[0] < 0 else 0
                    l = 1 if direction[1] > 0 else -1 if direction[1] < 0 else 0
                    pos = [i + k, j + l]
                    if self.InsideBounds(pos):
                        cPos = Tile(-1, -1)
                        if self.turn == 1:
                            j = self.width - 1
                            for i in range(self.height):
                                if self.board[i][j].ID == 0:
                                    cPos = Tile(i, j)
                                    continue
                        else:
                            j = 0
                            for i in range(self.height):
                                i = self.height - 1 - i
                                if self.board[i][j].ID == 0:
                                    cPos = Tile(i, j)
                                    continue
                        move = TileMovement([Tile(pos[0], pos[1]), cPos])
                        # Move tile to unoccupied cemetery slot
                        self.MoveTile(move, False, True, debug)
                        if debug: print(green + f"Moved tile at position {pos} to cemetery position {cPos} for board {repr(self)}" + white)
                        self.staleTurns = -1
                    else:
                        return False
            # Convert to king
            if  (
                    ((step.x == 0 or step.x == self.height - 1) and
                    abs(self.board[step.x][step.y].ID) != 2) and
                    not death
                ):
                    self.board[step.x][step.y].ID *= 2
                    self.staleTurns = -1
                    if debug: print(green + f"Promoted tile at position {prevStep} for board {repr(self)}" + white)
        else:
            return False
    def BuildMovementsTable(self, debug = False) -> list[list[list[TileMovement]]]:
        """Returns an array of lists with possible movements for the current board

        Returns:
            list[list[list[TileMovement]]]: Array of lists with possible movements
        """
        if debug: print(green + f"Building movements table for board {repr(self)}" + white)
        moveSet = [[[] for _ in range(self.width)] for _ in range(self.height)]
        for i, j in [(x, y) for x in range(0, self.height) for y in range(0, self.width - 2)]:
            iPos = Tile(i, j + 1)
            if (self.board[i][j + 1].ID == self.turn or self.board[i][j + 1].ID == 2 * self.turn):
                paths = self.ExtractMovements(iPos, debug = debug)
                for path in paths:
                    if path != []:
                        path.insert(0, iPos)
                        movement = TileMovement(path)
                        moveSet[i][j + 1].append(movement)
        return moveSet
    def ExtractMovements(self, pos: Tile, iPos: Tile = None,  path: list = None, paths: list = None, visited: list = None, debug: bool = False) -> list[list[Tile]]:
        """Searches recursively for every possible movement from a starting tile

        Args:
            pos (Tile): Current position to search
            iPos (Tile, optional): Initial search position. Defaults to None.
            path (list[Tile], optional): Current path being recorded. Defaults to None.
            paths (list[list[Tile]], optional): List of paths recorded. Defaults to None.
            visited (list[list[int]], optional): List of visited tiles. Defaults to None.

        Returns:
            list[list[Tile]]: List of all possible paths for the tile
        """ 
        assert self.InsideBounds([pos.x, pos.y]), red + f"Could not extract movements at {pos} because it is not inside the board" + white
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
            pos2 = Tile(pos.x + i, pos.y + j)
            #Checks if movement to tile would be valid, backtracks and saves positions accordingly
            if  (
                    not self.InsideBounds([pos2.x, pos2.y]) or
                    pos2 in visited
                ):
                if (path and path not in paths):
                    paths.append(path.copy())
                continue
            if  ( 
                    (abs(self.board[iPos.x][iPos.y].ID) != 2 and i == self.turn) or
                    self.board[pos2.x][pos2.y].ID == self.turn or
                    self.board[pos2.x][pos2.y].ID == self.turn * 2
                ):
                if  (path and path not in paths):
                    visited.append(pos2)
                    paths.append(path.copy())
                    path.pop()
                continue
            if (self.board[pos2.x][pos2.y].ID == 0):
                if (path == []):
                    path.append(pos2)
                    visited.append(pos2)
                    paths.append(path.copy())
                    path.pop()
                continue
            # Continues on the next tile after
            else:
                #Checks if movement to tile would be valid, backtracks and saves positions accordingly
                pos3 = Tile(pos2.x + i, pos2.y + j)
                if  (not self.InsideBounds([pos3.x, pos3.y])):
                    if (path and path not in paths):
                        paths.append(path.copy())
                        visited.append(pos2)
                    continue
                if self.board[pos3.x][pos3.y].ID != 0:
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
        """Analizes the changes from the current board to another board

        Args:
            other (Board): Board to be compared against

        Returns:
            list[list[int]]: Array containing values of 1 (to) or -1 (from) to indicate movement
        """
        assert isinstance(other, Board), red + f"Cannot find change values against {type(other).__name__}" + white
        assert self.height == other.height, red + "Could not find change values between different sized boards" + white
        if debug: print(green + f"Extracting change values from board {repr(self)} to board {repr(other)}" + white)
        values = [[[] for _ in range(self.width)] for _ in range(self.height)]
        for i, j in [(x, y) for x in range(0, self.height) for y in range(0, self.width)]:
            value = abs(other.board[i][j].ID) - abs(self.board[i][j].ID)
            if value != 0:
                value = value // abs(value)
            values[i][j] = value
        return values
    def FindMovement(self, other: Board, debug = False) -> TileMovement: #TODO testing
        """Searches for a possible movement that connects to another board

        Args:
            other (Board): Board to be compared against

        Returns:
            TileMovement: TileMovement that happened between boards, False if not found
        """
        assert self.height == other.height, red + "Could not find movement between different sized boards" + white
        assert self.height == other.height, red + "Could not find change values between different sized boards" + white
        changeValues = self.ExtractChangeValues(other, debug)
        for i, j in [(x, y) for x in range(0, self.height) for y in range(1, self.width - 1)]:
            if changeValues[i][j] == -1:
                paths = self.ExtractMovements(Tile(i, j), debug=debug)
                for path in paths:
                    path.insert(0, self.board[i][j])
                    boardClone = Board(self.turn, self.height)
                    boardClone.board = self.CreateClone(debug)
                    boardClone.MoveTile(TileMovement(path), debug=debug)
                    cloneChangeValues = self.ExtractChangeValues(boardClone, debug)
                    print(f"{cloneChangeValues} \n {changeValues}")
                    if cloneChangeValues == changeValues:
                        if debug: print(green + f"Found movement {path} between boards {repr(self)} and {repr(other)}" + white)
                        return path
        if debug: print(green + f"No movement found between boards {repr(self)} and {repr(other)}" + white)
        return False
    def ValidateMovement(self, movement: TileMovement, debug = False) -> bool:
        """Checks if a given movement is valid against all currently possible movements

        Args:
            movement (TileMovement): TileMovement to be validated

        Returns:
            bool:
        """
        paths = self.ExtractMovements(movement.steps[0], debug=debug) #Get movesTable
        for path in paths: #For each move
            path.insert(0, movement.steps[0])
            move = TileMovement(path)
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
        boardCopy = deepcopy(self.board)
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
    def PossibleMovements(self, pos: Tile, debug = False) -> tuple[str, list[TileMovement]]:
        """Returns a string detailing possible movements for a tile, to use in consoles. Also returns the list.

        Args:
            pos (Tile): Position of the tile to search in. Defaults to [-1, -1].

        Returns:
            tuple[str, list[TileMovement]]: Tuple containing the string and list form of possible movements
        """
        assert self.InsideBounds([pos.x, pos.y], False), red + f"Could not find movements at position {pos} because it is not inside the board" + white
        movesStr = ""
        movements = self.BuildMovementsTable(debug)
        movesStr += f"Movements available for tile at position {[pos.x + 1, pos.y]}:\n"
        for x in range(len(movements[pos.x][pos.y])):
            movesStr += f"{x + 1}: From {[pos.x + 1, pos.y]}"
            for step in movements[pos.x][pos.y][x].steps:
                movesStr += f" to {[step.x + 1, step.y]}"
            movesStr += "\n"
        if debug: print(green + f"Found movements {movements[pos.x][pos.y]} for board {repr(self)}" + white)
        return movesStr, movements[pos.x][pos.y]
    def IsStalemate(self, condition = 40, debug = False) -> bool: # ? 40 seems like a lot but it is tournament rules
        """Checks for stalemate conditions, returns True if game ended on stalemate

        Args:
            condition (int): Ammount of stale turns after which a stalemate is declared. Defaults to 10

        Returns:
            bool: Returns True if there is no possible movements or staleTurns is over condition
        """
        if debug: print(green + f"Checking for stalemate at turn [{self.turn}] with [{self.staleTurns}] stale turns for board {repr(self)}" + white)
        if self.staleTurns > condition or MiniMax(self, 1, debug=debug)[0] == TileMovement([Tile(-1, -1)]):
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
def MiniMax(board: Board, depth: int = None, bestMove: TileMovement = None, bestScore: int = None, mults = [10, 20], debug = False) -> tuple[TileMovement, int]:
    """Searches for the optimal movement(s) in a board and returns it (Random if multiple) along with it's assigned score
    Args:
        board (Board): Board to evaluate.
        depth (int): Depth of search, low values are recommended. Defaults to board's difficulty value.
        bestMove (TileMovement, optional): Highest scoring move found. Defaults to None.
        bestScore (int, optional): Highest scoring move's score value. Defaults to None.
        mults (list[int]): List of multipliers for score addition [movement, killing]. Defaults to [10, 20]
    Returns:
        tuple[TileMovement, int]: Tuple containing the optimal movement and its associated score
    """
    if debug: print(green + f"Initiating minimax algorithm for board {repr(board)} at depth [{depth}]" + white)
    # Initializes variables
    if depth is None:
        depth = board.difficulty
    if bestMove is None:
        bestMove = TileMovement([Tile(-1, -1)])
    # Last depth level, returns values found
    if depth == 0:
        return [bestMove, 0]
    # Algorithm
    if depth > 0:
        movesTable = board.BuildMovementsTable(debug)
        bestMoves = []
        # Check all movements of every tile that can move on the board
        for i, j in [(x, y) for x in range(0, board.height) for y in range(0, board.width - 2)]:
            j += 1
            if movesTable[i][j] == []:
                continue
            for movement in movesTable[i][j]:
                # Adds score and iterates
                score = AssignScore(movement, board, mults, debug)
                boardClone = Board(board.turn, board.height)
                boardClone.board = board.CreateClone(debug)
                boardClone.MoveTile(movement, debug=debug)
                boardClone.ChangeTurn(debug)
                score += MiniMax(boardClone, depth - 1, debug=debug)[1]
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
                bestMove = bestMoves[randint(0, len(bestMoves) - 1)]
        if bestScore == None:
            bestScore = 0
        if debug: print(green + f"Minimax has found movement {bestMove} with score [{bestScore}] for board {repr(board)}" + white)
        return bestMove, bestScore
def AssignScore(movement: TileMovement, board: Board, mults = [10, 20], debug = False) -> int:
    """Returns the total score sum for a given movement, uses hard coded values
    Args:
        movement (TileMovement): TileMovement to be appraised
        board (Board): Board where the movement is performed
        mults (list[int]): List of multipliers for score addition [movement, killing]. Defaults to [10, 20]
    Returns:
        int: Score calculated
    """
    score = 0
    prevStep = Tile(-1, -1)
    # Through every step in the movement
    for i in range(len(movement.steps)):
        step = movement.steps[i]
        if prevStep == Tile(-1, -1):
            prevStep == movement.steps[0]
            continue
        # Add movement score, doubled if converting
        if abs(board.board[step.x][step.y]) != 2:
            if step.x == 0 or step.x == board.height - 1:
                score += board.turn * mults[0]
            score += board.turn * mults[0]
        direction = [step.x - prevStep.x, step.y - prevStep.y]
        # Add killing score, doubled if king
        if  not (-1 <= direction[0] <=1):
            i = 1 if direction[0] > 0 else -1 if direction[0] < 0 else 0
            j = 1 if direction[1] > 0 else -1 if direction[1] < 0 else 0
            direction = [i, j]
            pos = [prevStep.x + direction.x, prevStep.y + direction.y]
            if board.InsideBounds(pos):
                if abs(board.board[pos[0]][pos[1]]) == 2:
                    score += board.turn * mults[1]
                score += board.turn * mults[1]
    if debug: print(green + f"Assigned score of [{score}] to movement {movement} for board {repr(board)}" + white)
    return score