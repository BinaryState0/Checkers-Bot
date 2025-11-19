from .color import Color
from checkersGame.board import Tile, Board
import cv2
import numpy
import math

_red = "\033[31m"
_blue = "\033[34m"
_white = "\033[37m"
_yellow = "\033[33m"
_green = "\033[32m"
_cyan = "\033[96m"

def Show(frame, id = "IMAGE", debug = False):
    """Opens a CV2 window to display a given frame
    Args:
        frame (numpy.array): Frame to be displayed
        id (str, optional): Display name of the given frame. Defaults to "IMAGE".
    """
    assert isinstance(id, str), _red + f"Display name for frame must be a string" + _white
    if debug:  print(_green + f"Showing frame with id {id}" + _white)
    cv2.imshow(id, frame) #Shows image
    cv2.waitKey(0) #Waits for input
    cv2.destroyAllWindows() #Closes window
def Contours(frame, color: Color, window = 0, threshold = 0, debug = False):
    """Returns an array of contours
    Args:
        frame (numpy.array): Frame to search for contours.
        color (Color, optional): Color to use for search.
        window (int, optional): Color range used. Defaults to 0.
        threshold (int, optional): Agressivenes of the search. Defaults to 0.
    Returns:
        list[]: Array of contours found.
    """
    assert 0 < threshold, _red + f"Threshold can not be [{threshold}], must be a value greater than 0" + _white
    if debug: print(_green + f"Searching for contours with color {color}" + _white)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, color.AsRange(window, True), color.AsRange(window, False))
    if debug: print(_green + f"{color.AsRange(window, True)} | {color.AsRange(window, False)}" + _white)
    if debug: Show(mask)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    if debug: Show(mask)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #Only keeps outermost contours
    if debug: print(_green + f"Found [{len(contours)}] unfiltered contours" + _white)
    filtered = []
    for c in contours:
        if debug: x, y, w, h = cv2.boundingRect(c)
        area = cv2.contourArea(c)
        if area > threshold:
            filtered.append(c)
            if debug: cv2.rectangle(mask, (x, y), (x + w, y + h), (0, 255, 0), 2)
    if debug: Show(mask)
    if debug: print(_green + f"Found [{len(filtered)}] filtered contours with threshold [{threshold}]" + _white)
    return filtered
def Centroid(contour, debug = False):
    """Returns the center coordinates of a contour using moments
    Args:
        contour (numpy.array): Contour which center must be found.
    Returns:
        list[int]: 2D Array with found coordinates.
    """
    M = cv2.moments(contour)
    if M["m00"] != 0: #Calculate centroid coordinates
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
    else: #Avoids division by 0 if area is 0
        cX, cY = 0, 0
    if debug: print(_green + f"Found center coordinates [{cX}, {cY}] for a contour" + _white)
    return (cX, cY)
def FindBoardCoords(frame, size = 6, debug = False) -> list[list[list[int]]]:
    """Finds the coordinates of a Nx(N+2) board.
    Args:
        frame (numpy.array): Image to search in.
        boardMarkers (Color): Color of the corner markers.
        size (int, optional): Size of the board (N). Defaults to 6.
        window (int, optional): Color range for corner markers. Defaults to 10.
        threshold (int, optional): Agressivenes of color filter. Defaults to 100.
    Returns:
        list[list[list[int]]]: Nx(N+2) Array of lists representing coordinates.
    """
    if debug: print(_green + f"Searching for board coordinates" + _white)
    coords = [[[] for _ in range(8)] for _ in range(6)]
    corners = []
    arDict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    arParams = cv2.aruco.DetectorParameters()
    mCorners, mIDs, _ = cv2.aruco.detectMarkers(frame, arDict, parameters=arParams)
    assert mIDs is not None, _red + "No ArUco markers detected" + _white
    cv2.aruco.drawDetectedMarkers(frame, mCorners, mIDs)
    if debug: Show(frame)
    mIDs = mIDs.flatten()
    expected_ids = [1, 2, 3, 4]
    found_ids = set(mIDs.tolist())
    missing = set(expected_ids) - found_ids
    assert not missing, _red + f"Missing ArUco markers: {missing}" + _white
    for i, id in enumerate(mIDs):
        if id in expected_ids:
            c = mCorners[i][0]
            centroid = numpy.mean(c, axis=0)  # average of the 4 corners
            corners.append(centroid)
    corners = numpy.array(corners, dtype=numpy.float32)
    corners = numpy.round(corners).astype(int)
    #Sort corners: top-left, top-right, bottom-right, bottom-left
    sum = corners.sum(axis=1)
    diff = numpy.diff(corners, axis=1)
    ordered = numpy.zeros((4, 2), dtype=numpy.float32)
    ordered[0] = corners[numpy.argmin(sum)] #top-left
    ordered[2] = corners[numpy.argmax(sum)] #bottom-right
    ordered[1] = corners[numpy.argmin(diff)] #top-right
    ordered[3] = corners[numpy.argmax(diff)] #bottom-left
    corners = ordered
    if debug: print(_green + f"Found corner coordinates {corners}" + _white)
    numRows, numCols = size + 2, size + 2
    cellSize = 20
    boardWidth = cellSize * numCols
    boardHeight = cellSize * numRows
    dstCorners = numpy.array([
        [0, 0], #top-left
        [boardWidth, 0], #top-right
        [boardWidth, boardHeight], #bottom-right
        [0, boardHeight] #bottom-left
    ], dtype=numpy.float32)
    M = cv2.getPerspectiveTransform(corners, dstCorners)
    MInv = numpy.linalg.inv(M)
    #This next block is credited to multiple stackoverflow posts and a touch of chatGPT (I have no idea what kind of math is happening here)
    for i, j in [(x, y) for x in range(numRows - 2) for y in range(numCols)]:
        #Normalized interpolation parameters inside the warped rectangle
        a = (i + 1) / (numRows - 1)  #vertical fraction (0 to 1)
        b = (j) / (numCols - 1)  #horizontal fraction (0 to 1)
        #Bilinear interpolation of the 4 corners in warped space
        posWarped = (
            (1 - a) * (1 - b) * dstCorners[0] +
            a * (1 - b) * dstCorners[3] + 
            a * b * dstCorners[2] +
            (1 - a) * b * dstCorners[1]
        )
        posHom = numpy.array([posWarped[0], posWarped[1], 1])
        posOrigHom = MInv @ posHom
        posOrigHom /= posOrigHom[2]
        posOrig = posOrigHom[:2].astype(int)
        coords[i][j] = posOrig
        if debug: cv2.circle(frame, tuple(posOrig), 5, (0, 0, 150), -1)
    if debug: Show(frame)
    return coords, corners
def ReadBoard(frame, player1: Color, player2: Color, coords: list[list[list[int]]], size = 6, debug = False) -> list[list[Tile]]:
    """Finds tiles in a frame and uses known board coordinates to construct a board of size Nx(N+2)
    Args:
        frame (numpy.array): Frame to search in.
        player1 (Color): Color of player1 Tiles (1).
        player2 (Color): Color of player2 Tiles (-1).
        coords (list[list[list[int]]]): Known board coordinates.
        size (int, optional): Size of the board (N). Defaults to 6.
    Returns:
        list[list[Tile]]: Board with ID values of each player's tile positions
    """
    if debug: print(_green + f"Reading board for players with color codes {player1} and {player2}" + _white)
    board = Board(0, size, debug)
    player1Tiles = Contours(frame, player1, 10, 100)
    player2Tiles = Contours(frame, player2, 10, 100)
    if debug: print(_green + f"Found [{len(player1Tiles)}] tiles for player1 and [{len(player2Tiles)}] tiles for player 2" + _white)
    for tile in player1Tiles:
        centroid = Centroid(tile, debug=debug)
        lowestDist = float("inf")
        tile = Tile(-1, -1, 1)
        for i, j in [(x, y) for x in range(0, size) for y in range(0, size + 2)]:
            target = [coords[i][j][0], coords[i][j][1]]
            dist = numpy.linalg.norm(centroid, target)
            if dist < lowestDist:
                lowestDist = dist
                tile.x, tile.y = i, j
        board[tile.x][tile.y] = tile
        if debug: print(_green + f"Assigned {tile}" + _white)
    for tile in player2Tiles:
        centroid = Centroid(tile, debug=debug)
        lowestDist = float("inf")
        tile = Tile(-1, -1, -1)
        for i, j in [(x, y) for x in range(0, size) for y in range(0, size + 2)]:
            target = [coords[i][j][0], coords[i][j][1]]
            dist = numpy.linalg.norm(centroid, target)
            if dist < lowestDist:
                lowestDist = dist
                tile.x, tile.y = i, j
        board[tile.x][tile.y] = tile
        if debug: print(_green + f"Assigned {tile}" + _white)
    if debug:
        foundBoard = Board(turn = 0, size = size, debug = debug)
        foundBoard.board = board.board
        print(_green + f"Board detected, printing simulated board:" + _white)
        print(foundBoard)
    return board.board