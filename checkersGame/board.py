from __future__ import annotations
from copy import deepcopy

_red = "\033[31m"
_blue = "\033[34m"
_white = "\033[37m"
_yellow = "\033[33m"
_green = "\033[32m"
_cyan = "\033[96m"

class Tile:
    """Abstract class to simplify Tile control"""
    def __init__(self, x: int = 0, y: int = 0, ID: int = 0):
        """Initializes the class

        Args:
            x (int, optional): X coordinate of the tile. Defaults to 0.
            y (int, optional): Y coordinate of the tile. Defaults to 0.
            ID (int, optional): ID of the tile. Defaults to 0.
        """
        assert isinstance(x, int) and isinstance(y, int), _red + "Tile coordinates must be an integer" + _white
        assert isinstance(ID, int), _red + "Tile ID must be an integer" + _white
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
            assert False, _red + f"Cannot compare {type(other).__name__} with Tile" + _white
        return self.x == other.x and self.y == other.y and self.ID == other.ID
class TileMovement:
    """Provides functionality to easily store and compare board movements"""
    def __init__(self, steps: list[Tile], debug = False):
        """Initializes class with a starting position

        Args:
            steps (List[Tile]): List of board tiles with respective coordinates, in order.
        """
        assert len(steps) > 0, _red + f"A movement must contain at least one step" + _white
        for step in steps:
            assert isinstance(step, Tile), _red + f"Steps must be of type {Tile}" + _white
        self.steps = steps
        if debug: print(_green + f"Created {TileMovement} with steps {steps}" + _white)
    def AddStep(self, step: Tile, debug = False):
        """Adds a step

        Args:
            step (Tile): Step to be added.
        """
        assert isinstance(step, Tile), _red + f"Steps must be of type {Tile}" + _white
        self.steps.append(step)
        if debug: print(_green + f"Added step {Tile} for movement {repr(self)}" + _white)
    def __eq__(self, other: TileMovement) -> bool:
        """Provides functionality to compare movements

        Args:
            other (TileMovement): TileMovement to compare against

        Returns:
            bool:
        """
        if  not isinstance(other, TileMovement):
            assert False, _red + f"Cannot compare {type(other).__name__} with TileMovement" + _white
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
        assert size % 2 == 0 and size > 0, _red + f"Attempted to create board {repr(self)} with invalid size" + _white
        self.width, self.height = size + 2, size
        self.board = [[Tile() for _ in range(size + 2)] for _ in range(size)]
        for i, j in [(x, y) for x in range(0, self.height) for y in range(0, self.width)]:
            self.board[i][j].x, self.board[i][j].y = i, j
        #Board configuration
        assert turn in range(-1, 2),  _red + f"Attempted to create board {repr(self)} with invalid turn ID" + _white
        self.turn = turn
        assert difficulty in range(1, 6), _red + f"Attempted to create board {repr(self)} with invalid difficulty" + _white
        self.difficulty = difficulty
        self.turnCount = 1
        self.staleTurns = 0
        if debug: print(_green + f"Creating board {repr(self)} at turn [{turn}] with size [{size}] at difficulty [{difficulty}]" + _white)
    def __str__(self) -> str:
        """Returns the board as a string, for use in console prints
        
        Returns:
            str: String representation of the board
        """
        boardStr = f"Turn: {self.turnCount} | To stalemate: {40 - self.staleTurns} | "
        if self.turn == 1:
            boardStr += _blue + "Blue moves" + _white + "\n"
        else:
            boardStr += _red + "Red moves" + _white + "\n"
        boardStr += _yellow
        for i in range(self.height + 4):
            if i == 0:
                boardStr += "c | x "
            elif i == self.height + 3:
                boardStr += "x | c "
            elif i == 1 or i == self.height + 2:
                boardStr += "| "
            else:
                boardStr += f"{i - 1} "
        boardStr += "\n" + _white
        for i in range(self.height):
            for j in range(self.width + 9):
                pos = [-1, -1]
                if j in [1, 3, self.width + 5, self.width + 3]:
                    boardStr += _yellow + "| " + _white
                elif j in [2, self.width + 4]:
                    boardStr += _yellow + f"{i + 1} " + _white
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
                    boardStr += _blue
                    if tile == 1:
                        boardStr += "o "
                    else:
                        boardStr += "O "
                    boardStr += _white
                else:
                    boardStr += _red
                    if tile == -1:
                        boardStr += "ø "
                    else:
                        boardStr += "Ø "
                    boardStr += _white
            boardStr += "\n"
        boardStr += _yellow
        for i in range(self.height + 4):
            if i == 0:
                boardStr += "c | x "
            elif i == self.height + 3:
                boardStr += "x | c "
            elif i == 1 or i == self.height + 2:
                boardStr += "| "
            else:
                boardStr += f"{i - 1} "
        boardStr += "\n" + _white
        return boardStr
    def SetBoard(self, debug = False):
        """Resets the board to an initial state, with 6 pieces per player arranged in a regular pattern"""
        self.turnCount = 1
        self.turn = 1
        self.staleTurns = 0
        if debug: print(_green + f"Resetting board {repr(self)} with size {self.height}" + _white)
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
        assert ID in range(-2, 3), _red + f"Could not count ammount of tiles with id {ID} as it is not a valid ID" + _white
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
        if debug: print(_green + f"Found a total of {count} tiles with id [{ID}] for board {repr(self)}" + _white)
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
            if debug: print(_green + f"Position {pos} is inside of board {repr(self)}" + _white)
            return True
        else:
            if debug: print(_green + f"Position {pos} is outside of board {repr(self)}" + _white)
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
        if debug: print(_green + f"Performing movement {movement} for board {repr(self)}" + _white)
        prevStep = Tile(-1, -1)
        if not validate or self.ValidateMovement(movement, debug):
            for step in movement.steps:
                if prevStep == Tile(-1, -1):
                    prevStep = step
                    continue
                # Perform movement
                i, j, k, l = prevStep.x, prevStep.y, step.x, step.y
                prevStep = step
                self.board[i][j].ID, self.board[k][l].ID = self.board[k][l].ID, self.board[i][j].ID
                if debug: print(_green + f"Swapped tiles at positions {[i, j]}, {[k, l]} for board {repr(self)}" + _white)
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
                        if debug: print(_green + f"Moved tile at position {pos} to cemetery position {cPos} for board {repr(self)}" + _white)
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
                    if debug: print(_green + f"Promoted tile at position {prevStep} for board {repr(self)}" + _white)
        else:
            return False
    def BuildMovementsTable(self, debug = False) -> list[list[list[TileMovement]]]:
        """Returns an array of lists with possible movements for the current board

        Returns:
            list[list[list[TileMovement]]]: Array of lists with possible movements
        """
        if debug: print(_green + f"Building movements table for board {repr(self)}" + _white)
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
        assert self.InsideBounds([pos.x, pos.y]), _red + f"Could not extract movements at {pos} because it is not inside the board" + _white
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
            if debug: print(_green + f"Searching movements at position {pos} in direction {[i, j]} for board {repr(self)}" + _white)
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
        if debug: print(_green + f"Found movements {paths} at position {iPos} for board {repr(self)}" + _white)
        return paths
    def ExtractChangeValues(self, other: Board, debug = False) -> list[list[int]]:
        """Analizes the changes from the current board to another board

        Args:
            other (Board): Board to be compared against

        Returns:
            list[list[int]]: Array containing values of 1 (to) or -1 (from) to indicate movement
        """
        assert isinstance(other, Board), _red + f"Cannot find change values against {type(other).__name__}" + _white
        assert self.height == other.height, _red + "Could not find change values between different sized boards" + _white
        if debug: print(_green + f"Extracting change values from board {repr(self)} to board {repr(other)}" + _white)
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
        assert self.height == other.height, _red + "Could not find movement between different sized boards" + _white
        assert self.height == other.height, _red + "Could not find change values between different sized boards" + _white
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
                        if debug: print(_green + f"Found movement {path} between boards {repr(self)} and {repr(other)}" + _white)
                        return path
        if debug: print(_green + f"No movement found between boards {repr(self)} and {repr(other)}" + _white)
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
                if debug: print(_green + f"Validated movement {movement} for board {repr(self)}" + _white)
                return True #True
        if debug: print(_green + f"Could not validate movement {movement} for board {repr(self)}" + _white)
        return False
    def CreateClone(self, debug = False) -> list[list[int]]:
        """Uses the deepcopy library to easily create a copy of the current board

        Returns:
            list[list[int]]: board value of the current Board
        """
        if debug: print(_green + f"Created deep copy of board {repr(self)}" + _white)
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
        if debug: print(_green + f"Advanced to turn [{self.turnCount}] for player ID [{self.turn}] at board {repr(self)}" + _white)
    def PossibleMovements(self, pos: Tile, debug = False) -> tuple[str, list[TileMovement]]:
        """Returns a string detailing possible movements for a tile, to use in consoles. Also returns the list.

        Args:
            pos (Tile): Position of the tile to search in. Defaults to [-1, -1].

        Returns:
            tuple[str, list[TileMovement]]: Tuple containing the string and list form of possible movements
        """
        assert self.InsideBounds([pos.x, pos.y], False), _red + f"Could not find movements at position {pos} because it is not inside the board" + _white
        movesStr = ""
        movements = self.BuildMovementsTable(debug)
        movesStr += f"Movements available for tile at position {[pos.x + 1, pos.y]}:\n"
        for x in range(len(movements[pos.x][pos.y])):
            movesStr += f"{x + 1}: From {[pos.x + 1, pos.y]}"
            for step in movements[pos.x][pos.y][x].steps:
                movesStr += f" to {[step.x + 1, step.y]}"
            movesStr += "\n"
        if debug: print(_green + f"Found movements {movements[pos.x][pos.y]} for board {repr(self)}" + _white)
        return movesStr, movements[pos.x][pos.y]
    def IsStalemate(self, condition = 40, debug = False) -> bool: # ? 40 seems like a lot but it is tournament rules
        """Checks for stalemate conditions, returns True if game ended on stalemate

        Args:
            condition (int): Ammount of stale turns after which a stalemate is declared. Defaults to 10

        Returns:
            bool: Returns True if there is no possible movements or staleTurns is over condition
        """
        from .minimax import MiniMax
        if debug: print(_green + f"Checking for stalemate at turn [{self.turn}] with [{self.staleTurns}] stale turns for board {repr(self)}" + _white)
        if self.staleTurns > condition or MiniMax(self, 1, debug=debug)[0] == TileMovement([Tile(-1, -1)]):
            if debug: print(_yellow + f"Found stalemate at turn [{self.turn}] with [{self.staleTurns}] stale turns for board {repr(self)}" + _white)
            return True
        return False
    def IsCheckmate(self, debug = False) -> bool:
        """Checks if there is any tiles remaining for the current player

        Returns:
            bool: True if tiles ammount is greater than 0
        """
        if debug: print(_green + f"Checking for checkmate at turn [{self.turn}] for board {repr(self)}" + _white)
        tiles = 0
        for i in [self.turn, self.turn * 2]:
            tiles += self.GetAmmountOf(i)
        if tiles == 0:
            if debug: print(_yellow + f"Found checkmate at turn [{self.turn}] for board {repr(self)}" + _white)
            return True
        return False