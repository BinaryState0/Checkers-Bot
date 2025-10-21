import cv2
import numpy
import math

#Color codes for console output
red = "\033[31m"
blue = "\033[34m"
white = "\033[37m"
yellow = "\033[33m"

class Color:
    def __init__(self, H = 0, S = 0, V = 0): #Initializes with HSV values
        self.H, self.S, self.V = H, S, V
    def AsArray(self): #Returns HSV values as array
        return [self.H, self.S, self.V]
    def AsRange(self,window= 0, isLow = True): #Returns low or high value of a window
        if isLow: return numpy.array([self.H - window, self.S - window, self.V - window])
        else: return numpy.array([self.H + window, self.S + window, self.V + window])
class Detection:
    def __init__(self): #Initializes camera
        pass
    def Show(frame, id = "IMAGE"): #Opens debug window showing frame, with name id
        cv2.imshow(id, frame) #Shows image
        cv2.waitKey(0) #Waits for input
        cv2.destroyAllWindows() #Closes window
    def Contours(frame, color = None,window= 0, threshold = 0): #Returns an array of contours from "frame", around hsv "color" +- "window", with tolerance "threshold"
        if color == None:
            color = [0, 0, 0]
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) #Converts image from RGB to HSV
        mask = cv2.inRange(hsv, color.AsRange(window, True), color.AsRange(window, False)) #Creates a binary mask with pixels in "window" of "color"
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #Finds contours in the binary image
        filtered = []
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            area = cv2.contourArea(c)
            if area > threshold:
                filtered.append(c)
                cv2.rectangle(mask, (x, y), (x + w, y + h), (0, 255, 0), 2)
        return filtered
    def Centroid(contour): #Returns coordinates of "contour" center point in camera coordinagtes
        M = cv2.moments(contour) #Extracts moments of contour
        if M["m00"] != 0: #Calculate centroid coordinates
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
        else: #Set centroid as (0, 0) if contour area == zero to avoid div==ion by zero
            cX, cY = 0, 0
        return [cX, cY]
    def Transform(coords, origin = [320, 480], scale = 0.81967, rotation = [180, 0, 90]): #Transforms coords, default to relevant coordinates
        coords = [coords[0], coords[1], 0]
        origin = [origin[0], origin[1], 0]
        coords = numpy.array(coords, dtype=numpy.float64) #Creates numpy arrays
        origin = numpy.array(origin, dtype=numpy.float64)
        relativeCoords = coords - origin #Translates to origin
        rx, ry, rz = numpy.deg2rad(rotation) #Transforms rotation to radians
        #Rotation arrays
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
        R = Rx @ Ry @ Rz #Combined rotation
        transformedCoords = scale * (R @ relativeCoords) #Applies rotation and scale to relative coords
        transformedCoords[1] = -1 * transformedCoords[1] #Inverts Y ax== for some reason
        transformedCoords = transformedCoords.astype(int) #Converts each value to an integer
        transformedCoords = transformedCoords.tolist() #Converts the np array to a list
        return transformedCoords
    def FindBoardCoords(frame, color,window= 10, threshold = 100): #Creates a 6x6 array of coordinates for the board, where "color" == the corner markers color
        coords = [[[] for _ in range(8)] for _ in range(6)] # 6x6 Array of empty lists
        corners = [] #Empty list of corner points
        contours = Detection.Contours(frame, color,window, threshold) #Detects contours of corner markers
        if len(contours) > 4: #Checks if contour list == 4 in lenght
            print(yellow + "Too many contours have been detected, couldnt parse board" + white)
            return False
        elif len(contours) < 4:
            print(yellow + "Too little contours have been detected, couldnt parse board" + white)
            return False
        for c in contours: #Add contour centroid to corners list
            centroid = Detection.Centroid(c)
            corners.append(centroid)
        corners = numpy.array(corners, dtype=numpy.float32) #Converts to numpy array
        # Sort corners: top-left, top-right, bottom-right, bottom-left
        s = corners.sum(axis=1)
        diff = numpy.diff(corners, axis=1)
        ordered = numpy.zeros((4, 2), dtype=numpy.float32)
        ordered[0] = corners[numpy.argmin(s)] #top-left
        ordered[2] = corners[numpy.argmax(s)] #bottom-right
        ordered[1] = corners[numpy.argmin(diff)] #top-right
        ordered[3] = corners[numpy.argmax(diff)] #bottom-left
        corners = ordered
        num_rows, num_cols = 6, 8
        cell_size = 20
        board_width = cell_size * num_cols #160
        board_height = cell_size * num_rows #120
        cell_width = board_width / num_cols
        cell_height = board_height / num_rows
        dstCorners = numpy.array([
            [0, 0], #top-left
            [board_width, 0], #top-right
            [board_width, board_height], #bottom-right
            [0, board_height] #bottom-left
        ], dtype=numpy.float32)
        M = cv2.getPerspectiveTransform(corners, dstCorners)
        MInv = numpy.linalg.inv(M)
        for i, j in [(x, y) for x in range(num_rows) for y in range(num_cols)]:
            # Normalized interpolation parameters inside the warped rectangle
            a = (i) / (num_rows - 1)  #vertical fraction (0 to 1)
            b = (j) / (num_cols - 1)  #horizontal fraction (0 to 1)
            # Bilinear interpolation of the 4 corners in warped space
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
            cv2.circle(frame, tuple(posOrig), 5, (0, 0, 150), -1)
        return coords
    def ReadBoard(frame, playerColor, AIColor, boardMarkers): #Returns a board with detected pieces
        board = [[0 for _ in range(8)] for _ in range(6)] #Empty 6x6 arraym
        playerTiles = Detection.Contours(frame, playerColor, 10, 100) #Obtain player tiles
        AITiles = Detection.Contours(frame, AIColor, 10, 100)
        coords = Detection.FindBoardCoords(frame, boardMarkers) #Obtain board coords
        for tile in playerTiles: #For each tile
            centroid = Detection.Centroid(tile) #Obtain centroid
            lowestDist = float("inf")
            tile = [-1, -1]
            for i, j in [(x, y) for x in range(0, 6) for y in range(0, 8)]: #For each board position
                dist = math.dist(centroid, coords[i][j]) #Calculate distance to tile
                if dist < lowestDist: #If lower than lowest distance, save it
                    lowestDist = dist
                    tile = [i, j]
            board[tile[0]][tile[1]] = 1 #Set board value at i, j to id
        for tile in AITiles: #For each tile
            centroid = Detection.Centroid(tile) #Obtain centroid
            lowestDist = float("inf")
            tile = [-1, -1]
            for i, j in [(x, y) for x in range(0, 6) for y in range(0, 8)]: #For each board position
                dist = math.dist(centroid, coords[i][j]) #Calculate distance to tile
                if dist < lowestDist: #If lower than lowest distance, save it
                    lowestDist = dist
                    tile = [i, j]
            board[tile[0]][tile[1]] = -1 #Set board value at i, j to id
        return board
