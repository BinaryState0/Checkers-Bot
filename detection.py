#from checkers import Board #Testing only
import cv2
import numpy as np
import math

class Color:
    def __init__(self, H = 0, S = 0, V = 0): #Initializes with HSV values
        self.H, self.S, self.V = H, S, V
    def AsArray(self): #Returns HSV values as array
        return [self.H, self.S, self.V]
    def AsRange(self, range = 0, isLow = True): #Returns low or high value of a range
        if isLow: return np.array([self.H - range, self.S - range, self.V - range])
        else: return np.array([self.H + range, self.S + range, self.V + range])
class Detection:
    def __init__(self): #Initializes camera
        pass
    def Show(frame, id = "IMAGE"): #Opens debug window showing frame, with name id
        cv2.imshow(id, frame) #Shows image
        cv2.waitKey(0) #Waits for input
        cv2.destroyAllWindows() #Closes window
    def Contours(frame, color = None, range = 0, threshold = 0): #Returns an array of contours from "frame", around hsv "color" +- "range", with tolerance "threshold"
        if color == None:
            color = [0, 0, 0]
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) #Converts image from RGB to HSV
        mask = cv2.inRange(hsv, color.AsRange(range, True), color.AsRange(range, False)) #Creates a binary mask with pixels in "range" of "color"
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
        coords = np.array(coords, dtype=np.float64) #Creates numpy arrays
        origin = np.array(origin, dtype=np.float64)
        relativeCoords = coords - origin #Translates to origin
        rx, ry, rz = np.deg2rad(rotation) #Transforms rotation to radians
        #Rotation arrays
        Rx = np.array([
            [1, 0, 0],
            [0, np.cos(rx), -np.sin(rx)],
            [0, np.sin(rx),  np.cos(rx)]
        ])
        Ry = np.array([
            [ np.cos(ry), 0, np.sin(ry)],
            [0, 1, 0],
            [-np.sin(ry), 0, np.cos(ry)]
        ])
        Rz = np.array([
            [np.cos(rz), -np.sin(rz), 0],
            [np.sin(rz),  np.cos(rz), 0],
            [0, 0, 1]
        ])
        R = Rx @ Ry @ Rz #Combined rotation
        transformedCoords = scale * (R @ relativeCoords) #Applies rotation and scale to relative coords
        transformedCoords[1] = -1 * transformedCoords[1] #Inverts Y ax== for some reason
        transformedCoords = transformedCoords.astype(int) #Converts each value to an integer
        transformedCoords = transformedCoords.tolist() #Converts the np array to a l==t
        return transformedCoords
    def FindBoardCoords(frame, color): #Creates a 6x6 array of coordinates for the board, where "color" == the corner markers color
        coords = [[[] for _ in range(6)] for _ in range(6)] # 6x6 Array of empty l==ts
        corners = [] #Empty l==t of corner points
        contours = Detection.Contours(frame, color, 10, 100) #Detects contours of corner markers
        if len(contours) > 4: #Checks if contour l==t == 4 in lenght
            print("Too big")
            return False
        elif len(contours) < 4:
            print("Too small")
            return False
        for c in contours: #Add contour centroid it to corners l==t
            centroid = Detection.Centroid(c)
            corners.append(centroid)
        corners = np.array(corners, dtype=np.float32) #Converts to numpy array
        s = corners.sum(axis=1) #Orders corners as Top-left, Top-right, Bottom-right, Bottom-left
        diff = np.diff(corners, axis=1)
        ordered = np.zeros((4,2), dtype=np.float32)
        ordered[0] = corners[np.argmin(s)]
        ordered[2] = corners[np.argmax(s)]
        ordered[1] = corners[np.argmin(diff)]
        ordered[3] = corners[np.argmax(diff)] 
        corners = ordered
        board_size = 100 #Distorts board to account for perspective
        dstCorners = np.array([
            [0, 0],
            [0, board_size],
            [board_size, board_size],
            [board_size, 0]
        ], dtype=np.float32)
        M = cv2.getPerspectiveTransform(corners, dstCorners)
        MInv = np.linalg.inv(M)
        for i, j in [(x, y) for x in range(0, 6) for y in range(0, 6)]: #For each tile coord
            a = (i + 0.5) / 6 #Get position constants
            b = (j + 0.5) / 6
            posWarped = (
            (1 - a) * (1 - b) * dstCorners[0] +
            a * (1 - b) * dstCorners[1] +
            a * b * dstCorners[2] +
            (1 - a) * b * dstCorners[3]
            ) #Calculates position
            posHom = np.array([posWarped[0], posWarped[1], 1]) #Warps the position back to perspective
            posOrigHom = MInv @ posHom
            posOrigHom /= posOrigHom[2]
            posOrig = posOrigHom[:2].astype(int) #converts to int
            coords[i][j] = posOrig #Saves the point
        return coords
    def ReadBoard(frame, playerColor, AIColor, boardMarkers): #Returns a board with detected pieces
        board = [[0 for _ in range(6)] for _ in range(6)] #Empty 6x6 arraym
        playerTiles = Detection.Contours(frame, playerColor, 10, 100) #Obtain player tiles
        AITiles = Detection.Contours(frame, AIColor, 10, 100)
        coords = Detection.FindBoardCoords(frame, boardMarkers) #Obtain board coords
        for tile in playerTiles: #For each tile
            centroid = Detection.Centroid(tile) #Obtain centroid
            lowestDist = float("inf")
            tile = [-1, -1]
            for i, j in [(x, y) for x in range(0, 6) for y in range(0, 6)]: #For each board position
                dist = math.dist(centroid, coords[i][j]) #Calculate distance to tile
                if dist < lowestDist: #If lower than lowest distance, save it
                    lowestDist = dist
                    tile = [i, j]
            board[tile[0]][tile[1]] = 1 #Set board value at i, j to id
        for tile in AITiles: #For each tile
            centroid = Detection.Centroid(tile) #Obtain centroid
            lowestDist = float("inf")
            tile = [-1, -1]
            for i, j in [(x, y) for x in range(0, 6) for y in range(0, 6)]: #For each board position
                dist = math.dist(centroid, coords[i][j]) #Calculate distance to tile
                if dist < lowestDist: #If lower than lowest distance, save it
                    lowestDist = dist
                    tile = [i, j]
            board[tile[0]][tile[1]] = -1 #Set board value at i, j to id
        return board

#Tested:
#frame = cv2.imread("frame_perspective.jpg")
#frame = cv2.resize(frame, (1280, 720), interpolation=cv2.INTER_AREA)
#green = Color(50, 150, 220)
#red = Color(0, 210, 255)
#gameBoard = Board()
#gameBoard.board = Detection.ReadBoard(frame, green, Color(50, 50, 50), red)
#print(gameBoard)
#coords = Detection.FindBoardCoords(frame, red)
#for i, j in [(x, y) for x in range(0, 6) for y in range(0, 6)]:
#    cv2.circle(frame, coords[i][j], radius=5, color=(255, 0, 0), thickness=-1)
#Detection.Show(frame)