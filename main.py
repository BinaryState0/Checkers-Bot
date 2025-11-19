from checkersGame.board import Board, Tile
from checkersGame.minimax import MiniMax
from checkersBot.control import Robot
from checkersBot.detection import FindBoardCoords, ReadBoard
from checkersBot.color import Color
from checkersBot.input import *
from mlf_api import RobotClient
from re import findall
import speech_recognition as sr

_red = "\033[31m"
_blue = "\033[34m"
_white = "\033[37m"
_yellow = "\033[33m"
_green = "\033[32m"
_cyan = "\033[96m"

RC = None
boardCoords = None
virtualBoard = Board(0)
prevBoard = Board(0)
currentBoard = Board(0)
playerColor = Color(164, 255, 255)
AIColor = Color(60, 255, 255)
debug = True

def Start():
    """Initial loop"""
    global markerColor, playerColor, AIColor, RC, virtualBoard, debug, boardCoords
    command = GetInput("str", "Select action: \n")
    if command == "Setup":
        print(_yellow + f"Initiating SETUP" + _white)
        rID = "10.200.145.10" + input("RC ID number: \n")
        client = RobotClient(rID)
        RC = Robot(client, True)
        if GetInput("bool", "Select new color values? (Y/N): \n"):
            markerColor = GetInput("color", "Insert board corner color (H, S, V): \n")
            playerColor = GetInput("color", "Insert player color (H, S, V): \n")
            AIColor = GetInput("color", "Insert AI color (H, S, V): \n")
        debug = GetInput("bool", "Enable debug information? (Y/N): \n")
        print(_yellow + f"Finished SETUP" + _white)
        Start()
    elif command == "Test ROB":
        frame = RC.MoveAndCapture(debug=True)
        boardCoords = FindBoardCoords(frame, markerColor, 6, 10, 100, debug=True)
        RC.TestMovement(boardCoords, True)
        Start()
    elif command == "Test MIC":
        voiceInput = FindVoiceInput(["hear me", "test", "wiggle", "hello"], debug=True)
        if voiceInput:
            RC.Emote(debug=True)
        Start()
    elif command == "Test CAM":
        RC.MoveAndCapture(debug=True)
        Start()
    elif command == "Play":
        Main()
        Start()
    else:
        Start()
def Main():
    global markerColor, playerColor, AIColor, RC, virtualBoard, debug, boardCoords
    """Main loop"""
    if virtualBoard.turn == 0:
        boardCoords = FindBoardCoords(RC.MoveAndCapture(debug), markerColor, debug=debug)
        prevBoard.board = ReadBoard(RC.MoveAndCapture(debug=debug), playerColor, AIColor, boardCoords, debug=debug)
        virtualBoard.SetBoard(debug)
        for movement in RC.MoveToBoard(prevBoard, virtualBoard, debug):
            RC.MoveRobot(movement, debug=debug)
        Main()
    else:
        if virtualBoard != prevBoard:
            RC.Emote("no", debug=debug)
            for movement in RC.MoveToBoard(prevBoard, virtualBoard, debug):
                RC.MoveRobot(movement, debug=debug)
            Main()
        if virtualBoard.turn == 1:
            if virtualBoard.IsCheckmate(debug) or virtualBoard.IsStalemate(20, debug=debug):
                RC.Emote("dance", 30, debug=debug)
                virtualBoard.turn = 0
                Main()
            RC.Emote()
            voiceInput = False
            while voiceInput == False:
                voiceInput = FindVoiceInput(["turn, finished, done, ready"], debug=debug)
            currentBoard.board = ReadBoard(RC.MoveAndCapture(debug=debug), playerColor, AIColor, boardCoords, debug=debug)
            movement = virtualBoard.FindMovement(currentBoard, debug)
            if movement is not False:
                if virtualBoard.MoveTile(movement, debug=debug) is not False:
                    virtualBoard.MoveTile(movement, debug=debug)
                    virtualBoard.ChangeTurn(debug)
                    RC.Emote("yes", debug=debug)
                    prevBoard.board = ReadBoard(RC.MoveAndCapture(debug=debug), playerColor, AIColor, boardCoords, debug=debug)
                    Main()
            virtualBoard.board = prevBoard.board
            RC.Emote("no", debug=debug)
            for movement in RC.MoveToBoard(currentBoard, prevBoard, debug):
                RC.MoveRobot(movement, debug=debug)
            prevBoard.board = ReadBoard(RC.MoveAndCapture(debug=debug), playerColor, AIColor, boardCoords, debug=debug)
            Main()
        else:
            if virtualBoard.IsCheckmate(debug) or virtualBoard.IsStalemate(debug=debug):
                RC.Emote("no", 30, debug=debug)
                virtualBoard.turn = 0
                Main()
            movement, _ = MiniMax(virtualBoard, debug=debug)
            movement3D = RC.Movement2Dto3D(movement, debug)
            RC.MoveRobot(movement3D, debug=debug)
            virtualBoard.MoveTile(movement, debug=debug)
            currentBoard.board = ReadBoard(RC.MoveAndCapture(debug=debug), playerColor, AIColor, boardCoords, debug=debug)
            for i, j in [(x, y) for x in range(0, virtualBoard.height) for y in range(0, virtualBoard.height)]:
                j += 1
                if virtualBoard.board[i][j] == currentBoard.board[i][j]:
                    continue
                else:
                    RC.Emote("no", debug=debug)
                    virtualBoard.MoveTile(movement.Reversed(), debug=debug)
                    for move in RC.MoveToBoard(currentBoard, virtualBoard, debug):
                        RC.MoveRobot(move, debug=debug)
                    Main()
            RC.Emote("yes", debug=debug)
            for move in RC.MoveToBoard(currentBoard, virtualBoard, debug):
                RC.MoveRobot(move, debug=debug)
            RC.MoveToBoard(currentBoard, virtualBoard)
            virtualBoard.ChangeTurn(debug)
            print(virtualBoard)
            Main()
Start()