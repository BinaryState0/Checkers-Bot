from __future__ import annotations
from mlf_api import RobotClient
from time import sleep
from checkersGame.board import Tile, TileMovement, Board
from .detection import Show
import numpy
import cv2

_red = "\033[31m"
_blue = "\033[34m"
_white = "\033[37m"
_yellow = "\033[33m"
_green = "\033[32m"
_cyan = "\033[96m"

#TODO tweak values
_Hover = 40
_Contact = 20

def Transform(coords, origin: list[int] = [310, 390, 0], scale: int = 0.81967, rotation: list[int] = [180, 0, 270], debug = False) -> list[int]: 
    """Transforms between camera and robot coordinates
    Args:
        coords (list[int]): X, Y, Z coordinates to transform.
        origin (list[int]): X, Y, Z coordinates of the target system.
        scale (int): Scale constant between systems.
        rotation (list[int]): X, Y, Z rotations to apply between systems.
    Returns:
        list[int]: Transformed coordinates
    """
    assert len(coords) == 3, _red + f"Coordinates must have 3 values." + _white
    assert len(rotation) == 3, _red + f"Rotation must have 3 axis." + _white
    assert 0 < scale, _red + f"Scale must be greater than 0." + _white
    if debug: print(_green + f"Transforming coordinates {coords} to system with origin {origin}, scale {scale} and reltive rotation {rotation}" + _white)
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
    transformedCoords = numpy.round(transformedCoords).astype(int)
    transformedCoords = transformedCoords.tolist()
    if debug: print(_green + f"Calculated coordinates as {transformedCoords}" + _white)
    return transformedCoords
class Tile3D:
    """Abstract class to simplify Tile control"""
    def __init__(self, x: int = 0, y: int = 0, z: int = 0, ON: bool = False):
        """Initializes the class

        Args:
            x (int, optional): X coordinate of the tile. Defaults to 0.
            y (int, optional): Y coordinate of the tile. Defaults to 0.
            z (int, optional): Z coordinate of the tile. Defaults to 0.
            ON (bool, optional): Action ON/OFF. Defaults to False (OFF).
        """
        assert isinstance(x, int) and isinstance(y, int) and isinstance(z, int), _red + "Tile coordinates must be an integer" + _white
        self.x, self.y, self.z = x, y, z
        assert isinstance(ON, bool), _red + "Tile ON status must be a boolean" + _white
        self.ON = ON
    def __repr__(self):
        string = f"Tile3D[{self.x}, {self.y}, {self.z}]"
        if self.ON: string += "(1)"
        else: string += "(0)"
        return string
    def __eq__(self, other):
        """Provides functionality to compare tiles

        Args:
            other (Tile3D): Tile3D to compare against

        Returns:
            bool:
        """
        if  not isinstance(other, Tile3D):
            assert False, _red + f"Cannot compare {type(other).__name__} with Tile" + _white
        return self.x == other.x and self.y == other.y and self.z == other.z and self.ON == other.ON
class Tile3DMovement:
    """Provides functionality to easily store and compare 3D movements"""
    def __init__(self, steps: list[Tile3D], debug = False):
        """Initializes class with a starting position

        Args:
            steps (List[Tile3D]): List of 3D tiles with respective coordinates, in order.
        """
        assert len(steps) > 0, _red + f"A movement must contain at least one step" + _white
        for step in steps:
            assert isinstance(step, Tile3D), _red + f"Steps must be of type {Tile3D}" + _white
        self.steps = steps
        if debug: print(_cyan + f"Created {Tile3DMovement} with steps {steps}" + _white)
    def AddStep(self, step: Tile3D, debug = False):
        """Adds a step

        Args:
            step (Tile): Step to be added.
        """
        assert isinstance(step, Tile3D), _red + f"Steps must be of type {Tile3D}" + _white
        self.steps.append(step)
        if debug: print(_cyan + f"Added step {Tile3D} for movement {repr(self)}" + _white)
    def __eq__(self, other: Tile3DMovement) -> bool:
        """Provides functionality to compare 3D movements

        Args:
            other (Tile3DMovement): Tile3DMovement to compare against

        Returns:
            bool:
        """
        if  not isinstance(other, Tile3DMovement):
            assert False, _red + f"Cannot compare {type(other).__name__} with Tile3DMovement" + _white
        return self.steps == other.steps
    def __str__(self):
        return f"Tile3DMovement({str(self.steps)})"
class Robot:
    """Controls robot interactions"""
    def __init__(self, rClient: RobotClient, debug = False):
        """Initializes the robot class with a provided RobotClient.

        Args:
            rClient (RobotClient): The robot client to utilize.
            relay (int, optional): Relay to connect for controlling actions. Defaults to 1
        """
        assert rClient.connected, _red + f"The client must be connected to initialize a Robot class" + _white
        self.rClient = rClient
        if debug: print(_cyan + f"Initialized robot client {repr(self)} with address [{rClient.address}]" + _white)
    def MoveRobot(self, movement: Tile3DMovement, delay: int = 1, debug = False):
        """Follows a Tile3DMovement with the robot

        Args:
            movement (Tile3DMovement): Tile3DMovement to follow with the robot hand
            delay (int, optional): Movement delay in seconds. Defaults to 1.
        """
        if debug: print(_cyan + f"Following {movement} with RC {self.rClient.address}" + _white)
        for step in movement.steps:
            self.rClient.move_xyz(step.x, step.y, step.z)
            sleep(delay)
            self.rClient.set_relay_status(step.ON)
            if debug: print(_cyan + f"Moved RC [{self.rClient.address}] to position {step}" + _white)
        self.rClient.home()
        if debug: print(_cyan + f"RC {self.rClient.address} has finished moving and now returned to its home position" + _white)
        sleep(delay)
    def MoveAndCapture(self, delay: int = 1, debug = False):
        """Captures a frame from the RC camera, if debug is ON saves the image as a file.

        Args:
            delay (int, optional): Movement delay for robot. Defaults to 1.

        Returns:
            numpy.array: Frame captured by the RC camera.
        """
        if debug: print(_cyan + f"Initiating camera capture with RC {self.rClient.address}" + _white)
        if debug: print(_cyan + f"Moving RC [{self.rClient.address}] out of the way" + _white)
        self.rClient.set_joints(0)
        sleep(delay)
        if debug: print(_cyan + f"Saving image from RC [{self.rClient.address}] camera" + _white)
        frame = self.rClient.capture()
        if debug: Show(frame, f"RAWIMAGE from RC [{self.rClient.address}]")
        self.rClient.home()
        if debug:
            from datetime import datetime
            cv2.imwrite(f"../IMAGES/CAPTURE{datetime.now().strftime('%d%m%Y%H%M')}.jpeg", frame)
        print(_cyan + f"RC {self.rClient.address} has saved an image and is returning to its home position" + _white)
        sleep(delay)
        return frame
    def Movement2Dto3D(self, movement: TileMovement, debug = False):
        """Converts a 2D TileMovement from the checkers module to a Tile3DMovement

        Args:
            movement (TileMovement): Movement to convert.

        Returns:
            Tile3DMovement: Converted movement.
        """
        if debug: print(_cyan + f"Converting {movement} to {Tile3DMovement}" + _white)
        steps = []
        for step in movement.steps:
            if debug: print(_cyan + f"Converting {step}" + _white)
            pos = [step.x, step.y, 0]
            pos = Transform(pos, debug=debug)
            step1 = Tile3D(pos[0], pos[1], _Hover, True)
            step2 = Tile3D(pos[0], pos[1], _Contact, False)
            if next is not None:
                step3 = Tile3D(pos[0], pos[1], _Contact, True)
                step4 = Tile3D(pos[0], pos[1], _Hover, True)
            steps.extend([step1, step2, step3, step4])
        movementConverted = Tile3DMovement(steps, debug)
        return movementConverted 
    def TestMovement(self, coords: list[list[list[int]]], debug = False):
        """Tests RC movement over known coordinates of a board

        Args:
            coords (list[list[list[int]]]): Known board coordinates
        """
        assert coords is not None, _red + f"Coordinates for RC {self.rClient.address} cant be null" + _white
        if debug: print(_cyan + f"Testing board movement for RC {self.rClient.address}" + _white)
        steps = []
        for i, j in [(x, y) for x in range(0, len(coords)) for y in range(0, len(coords[x]))]:
            pos = [coords[i][j][0], coords[i][j][1]]#Transform([coords[i][j][0], coords[i][j][1], 0], debug=debug)
            steps.append(Tile(int(pos[0]), int(pos[1])))
        movement2d = TileMovement(steps, debug)
        movement3d = self.Movement2Dto3D(movement2d, debug)
        self.MoveRobot(movement3d, 0.5, debug=debug)
        if debug: print(_cyan + f"Finished testing for RC {self.rClient.address}" + _white)
    def Emote(self, emote: str = "hi", length = 10, delay = 1, debug = False):
        """Predefined movements for the RC to perform

        Args:
            emote (str, optional): String defining the emote to perform. Defaults to "hi".
            length (int, optional): Duration/repetitions of the emote. Defaults to 10.
            delay (int, optional): Movement delay. Defaults to 1.
        """
        if emote == "hi":
            self.rClient.set_joints(0, 30, 60)
            sleep(delay)
            for i in range(length):
                if i % 2 == 0:
                    self.rClient.set_joints(q3=100)
                    sleep(delay/2)
                else:
                    self.rClient.set_joints(q3=140)
                    sleep(delay/2)
            self.rClient.home()
            sleep(delay)
        if emote == "yes":
            for i in range(length):
                if i % 2 == 0:
                    self.rClient.set_joints(q1=70)
                    sleep(delay)
                else:
                    self.rClient.set_joints(q1=110)
                    sleep(delay)
            self.rClient.home()
            sleep(delay)
        if emote == "no":
            for i in range(length):
                if i % 2 == 0:
                    self.rClient.set_joints(q0=70)
                    sleep(delay)
                else:
                    self.rClient.set_joints(q0=110)
                    sleep(delay)
            self.rClient.home()
            sleep(delay)
        if emote == "dance":
            from random import randint
            for i in range(length):
                q0, q1, q2, = [randint(45, 135) for _ in range(3)]
                self.rClient.set_joints(q0, q1, q2)
                sleep(delay)
            self.rClient.home()
            sleep(delay)
    def MoveToBoard(self, prevBoard: Board, targetBoard: Board, debug = False) -> TileMovement:
        """Generates a movemement that moves all the pieces in the board to match another state.

        Args:
            prevBoard (Board): Board to move from.
            targetBoard (Board): Board to move to.

        Returns:
            TileMovement: Movement generated.
        """
        changedTiles = []
        movements = []
        changeTable = prevBoard.ExtractChangeValues(targetBoard, debug)
        for i, j in [(x, y) for x in range(0, targetBoard.height) for y in range(0, targetBoard.width)]:
            if changeTable[i][j] == 1:
                tileTo = targetBoard[i][j]
            elif changeTable[i][j] == -1:
                tileFrom = prevBoard[i][j]
            else:
                continue
            changedTiles.extend([tileTo, tileFrom])
        while len(changedTiles) > 0:
            for tile in changedTiles:
                if changeTable[tile.x][tile.y] == -1:
                    tileFrom = tile
                    changedTiles.remove(tileFrom)
                    break
            for tile in changedTiles:
                if changeTable[tile.x][tile.y] == 1 and tileFrom.ID // abs(tileFrom.ID) == tile.ID // abs(tile.ID):
                    tileTo = tile
                    changedTiles.remove(tileTo)
                    break
            movements.append(self.Movement2Dto3D(TileMovement(tileFrom, tileTo, debug)))
        return movements