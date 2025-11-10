from .board import Board, TileMovement, Tile
from random import randint

_red = "\033[31m"
_blue = "\033[34m"
_white = "\033[37m"
_yellow = "\033[33m"
_green = "\033[32m"
_cyan = "\033[96m"

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
    if debug: print(_green + f"Initiating minimax algorithm for board {repr(board)} at depth [{depth}]" + _white)
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
        if debug: print(_green + f"Minimax has found movement {bestMove} with score [{bestScore}] for board {repr(board)}" + _white)
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
    if debug: print(_green + f"Assigned score of [{score}] to movement {movement} for board {repr(board)}" + _white)
    return score