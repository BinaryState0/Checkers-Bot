from __future__ import annotations
from constants import *
import cv2
import numpy
import math

class Color:
    """Stores 3 values representing a color with HSV codes"""
    def __init__(self, H = 0, S = 0, V = 0):
        """Initializes Color class.

        Args:
            H (int, optional): Hue. Defaults to 0.
            S (int, optional): Saturation. Defaults to 0.
            V (int, optional): Value. Defaults to 0.
        """
        assert 0 <= H <= 255, red + f"Hue for color {repr(self)} must be bewteen 0 and 255" + white
        assert 0 <= S <= 255, red + f"Saturation for color {repr(self)} must be bewteen 0 and 255" + white
        assert 0 <= V <= 255, red + f"Value for color {repr(self)} must be bewteen 0 and 255" + white
        self.H, self.S, self.V = H, S, V
    def AsArray(self) -> list[int]:
        """Returns the values of the color as an array.

        Returns:
            list[int]: Values H, S and V as an array.
        """
        return [self.H, self.S, self.V]
    def AsRange(self, window = 0, isLow = True) -> numpy.array:
        """Returns low or high value around acolor with range "window" as a numpy array

        Args:
            window (int, optional): Range. Defaults to 0.
            isLow (bool, optional): If true, return lowest value. Defaults to True.

        Returns:
            numpy.array: Lowest or highest array of values HSV.
        """
        assert 0 <= window <= 255, red + f"Window range for color {repr(self)} must be bewteen 0 and 255" + white
        if isLow: return numpy.array([self.H - window, self.S - window, self.V - window])
        else: return numpy.array([self.H + window, self.S + window, self.V + window])
    def __str__(self) -> str:
        """Representation of Color class as string

        Returns:
            str: String with HSV values
        """
        colorStr = f"Color({self.H}, {self.S}, {self.V})"
        return colorStr
class Detection:
    """Handles detection of a Nx(N+2) board based on it's 4 corners"""
    def Show(frame, id = "IMAGE", debug = False):
        """Opens a CV2 window to display a given frame

        Args:
            frame (numpy.array): Frame to be displayed
            id (str, optional): Display name of the given frame. Defaults to "IMAGE".
        """
        assert isinstance(id, str), red + f"Display name for frame must be a string" + white
        if debug:  print(green + f"Showing frame with id {id}" + white)
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
        assert 0 < threshold, red + f"Threshold can not be [{threshold}], must be a value greater than 0" + white
        if debug: print(green + f"Searching for contours with color {Color}" + white)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, color.AsRange(window, True), color.AsRange(window, False))
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #Only keeps outermost contours
        if debug: print(green + f"Found [{len(contours)}] unfiltered contours" + white)
        filtered = []
        for c in contours:
            if debug: x, y, w, h = cv2.boundingRect(c)
            area = cv2.contourArea(c)
            if area > threshold:
                filtered.append(c)
                if debug: cv2.rectangle(mask, (x, y), (x + w, y + h), (0, 255, 0), 2)
        if debug: Detection.Show(mask)
        if debug: print(green + f"Found [{len(filtered)}] filtered contours with threshold [{threshold}]" + white)
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
        if debug: print(green + f"Found center coordinates [{cX}, {cY}] for a contour" + white)
        return [cX, cY]
    def Transform(coords, origin: list[int], scale: int, rotation: list[int], debug = False) -> list[int]: 
        """Transforms between two coordinate systems

        Args:
            coords (list[int]): X, Y, Z coordinates to transform.
            origin (list[int]): X, Y, Z coordinates of the target system.
            scale (int): Scale constant between systems.
            rotation (list[int]): X, Y, Z rotations to apply between systems.

        Returns:
            list[int]: Transformed coordinates
        """
        assert len(coords) == 3, red + f"Coordinates must have 3 values." + white
        assert len(coords) == 3, red + f"Coordinates must have 3 values." + white
        assert len(coords) == 3, red + f"Rotation must have 3 axis." + white
        assert 0 < scale, red + f"Scale must be greater than 0." + white
        if debug: print(green + f"Transforming coordinates {coords} to system with origin {origin}, scale {scale} and reltive rotation {rotation}" + white)
        coords = [coords[0], coords[1], coords[2]]
        origin = [origin[0], origin[1], origin[2]]
        coords = numpy.array(coords, dtype=numpy.float64)
        origin = numpy.array(origin, dtype=numpy.float64)
        relativeCoords = coords - origin
        rx, ry, rz = numpy.deg2rad(rotation)
        Rx = numpy.array([
            [1, 0, 0],
            [0, numpy.cos(rx), -numpy.sin(rx)],
            [0, numpy.sin(rx),  numpy.cos(rx)]
        ])
        Ry = numpy.array([
            [ numpy.cos(ry), 0, numpy.sin(ry)],
            [0, 1, 0],
            [-numpy.sin(ry), 0, numpy.cos(ry)]
        ])
        Rz = numpy.array([
            [numpy.cos(rz), -numpy.sin(rz), 0],
            [numpy.sin(rz),  numpy.cos(rz), 0],
            [0, 0, 1]
        ])
        R = Rz @ Ry @ Rx #Applies rotation on X, then Y, then Z
        transformedCoords = scale * (R @ relativeCoords)
        transformedCoords[1] = -1 * transformedCoords[1] #Y axis is inverted to account for coordinate system handedness differences
        transformedCoords = numpy.round(transformedCoords).astype(int)
        transformedCoords = transformedCoords.tolist()
        if debug: print(green + f"Calculated coordinates as {transformedCoords}" + white)
        return transformedCoords
    def FindBoardCoords(frame, boardMarkers: Color, size = 6, window = 10, threshold = 100, debug = False) -> list[list[list[int]]]:
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
        if debug: print(green + f"Searching for board coordinates" + white)
        coords = [[[] for _ in range(8)] for _ in range(6)]
        corners = []
        contours = Detection.Contours(frame, boardMarkers, window, threshold, debug=debug) #Detects contours of corner markers
        assert len(contours) < 5, red + f"Corner identification found too many contours, sdearch values must be tweaked." + white
        assert len(contours) > 3, red + f"Corner identification found too few contours, sdearch values must be tweaked." + white
        for c in contours:
            centroid = Detection.Centroid(c)
            corners.append(centroid)
        corners = numpy.array(corners, dtype=numpy.float32)
        #Sort corners: top-left, top-right, bottom-right, bottom-left
        sum = corners.sum(axis=1)
        diff = numpy.diff(corners, axis=1)
        ordered = numpy.zeros((4, 2), dtype=numpy.float32)
        ordered[0] = corners[numpy.argmin(sum)] #top-left
        ordered[2] = corners[numpy.argmax(sum)] #bottom-right
        ordered[1] = corners[numpy.argmin(diff)] #top-right
        ordered[3] = corners[numpy.argmax(diff)] #bottom-left
        corners = ordered
        if debug: print(green + f"Found corner coordinates {corners}" + white)
        numRows, numCols = size, size + 2
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
        for i, j in [(x, y) for x in range(numRows) for y in range(numCols)]:
            #Normalized interpolation parameters inside the warped rectangle
            a = (i) / (numRows - 1)  #vertical fraction (0 to 1)
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
        if debug: Detection.Show(frame)
        return coords
    def ReadBoard(frame, player1: Color, player2: Color, coords: list[list[list[int]]], size = 6, debug = False) -> list[list[int]]:
        """Finds tiles in a frame and uses known board coordinates to construct a board of size Nx(N+2)

        Args:
            frame (numpy.array): Frame to search in.
            player1 (Color): Color of player1 Tiles (1).
            player2 (Color): Color of player2 Tiles (-1).
            coords (list[list[list[int]]]): Known board coordinates.
            size (int, optional): Size of the board (N). Defaults to 6.

        Returns:
            list[list[int]]: Board with ID values of each player's tile positions
        """
        if debug: print(green + f"Reading board for players with color codes {player1} and {player2}" + white)
        board = [[0 for _ in range(8)] for _ in range(6)]
        player1Tiles = Detection.Contours(frame, player1, 10, 100)
        player2Tiles = Detection.Contours(frame, player2, 10, 100)
        if debug: print(green + f"Found [{len(player1Tiles)}] tiles for player1 and [{len(player2Tiles)}] tiles for player 2" + white)
        for tile in player1Tiles:
            centroid = Detection.Centroid(tile, debug=debug)
            lowestDist = float("inf")
            tile = [-1, -1]
            for i, j in [(x, y) for x in range(0, 6) for y in range(0, 8)]:
                dist = math.dist(centroid, coords[i][j])
                if dist < lowestDist:
                    lowestDist = dist
                    tile = [i, j]
            board[tile[0]][tile[1]] = 1
            if debug: print(green + f"Assigned a tile to player1 at coords [{tile[0]}, {tile[1]}]" + white)
        for tile in player2Tiles:
            centroid = Detection.Centroid(tile, debug=debug)
            lowestDist = float("inf")
            tile = [-1, -1]
            for i, j in [(x, y) for x in range(0, 6) for y in range(0, 8)]:
                dist = math.dist(centroid, coords[i][j])
                if dist < lowestDist:
                    lowestDist = dist
                    tile = [i, j]
            board[tile[0]][tile[1]] = -1
            if debug: print(green + f"Assigned a tile to player2 at coords [{tile[0]}, {tile[1]}]" + white)
        if debug:
            from checkers import Board
            foundBoard = Board(turn = 0, size = size, debug = debug)
            foundBoard.board = board
            print(green + f"Board detected, printing simulated board:" + white)
            print(foundBoard)
        return board
