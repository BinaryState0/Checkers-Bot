from checkersGame.board import Board, Tile
from checkersGame.minimax import MiniMax
from checkersBot.control import Robot
from checkersBot.detection import FindBoardCoords, ReadBoard
from checkersBot.color import Color
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
markerColor = Color()
playerColor = Color()
AIColor = Color()
debug = False

def GetInput(type: str, message: str):
    """Unified function to obtain different types of input from the user

    Args:
        type (str): Type of input to be detected
        message (str): Message to display

    Returns:
        any: Input returned
    """
    userInput = input(message)
    if type == "int":
        if userInput.isnumeric():
            return int(userInput)
        else:
            input(_yellow + "Invalid input, press enter to try again" + _white)
            return GetInput(type, message)
    elif type == "str":
        return userInput
    elif type == "bool":
        if "Y" == userInput:
            return True
        elif "N" == userInput:
            return False
        else:
            input(_yellow + "Invalid input, press enter to try again" + _white)
        return GetInput(type, message)
    elif type == "pos":
        inputPos = findall(r'\d+', userInput)
        inputPos = [int(x) for x in inputPos]
        if len(inputPos) != 2:
            input(_yellow + "Invalid input, press enter to try again" + _white)
            return GetInput(type, message)
        inputPos[0] -= 1
        return inputPos
    elif type == "color":
        inputPos = findall(r'\d+', userInput)
        inputPos = [int(x) for x in inputPos]
        if len(inputPos) != 3:
            input(_yellow + "Invalid input, press enter to try again" + _white)
            return GetInput(type, message)
        inputPos[0] -= 1
        return inputPos
def FindVoiceInput(keywords: list[str], micID: int = 9, debug = False) -> bool:
    """Attempts to use the microphone to obtain input

    Args:
        keywords (list[str]): List of keywords to look for
        micID (int, optional): Microphone ID to be used. Defaults to 9.

    Returns:
        bool: If keyword was found or not
    """
    rec = sr.Recognizer()
    mic = sr.Microphone(device_index=micID)
    if debug: print(_yellow + f"Initializing audio input search for keywords '{keywords}'" + _white)
    with mic as source:
        rec.adjust_for_ambient_noise(source)
        while(True):
            #audio = rec.listen(source, phrase_time_limit=3)
            try:
                audio = rec.listen(source, timeout=2, phrase_time_limit=2)
            except sr.WaitTimeoutError:
                if debug: print(_red + f"Audio detection timeout, trying again" + _white)
                continue
            try:
                text = rec.recognize_google(audio, language="en-US").lower()
                if debug: print(_yellow + f"Microphone recognize audio '{text}'" + _white)
                if any(k in text for k in keywords):
                    if debug: print(_yellow + f"Keyword detected succesfully" + _white)
                    return True
            except sr.UnknownValueError:
                pass
            except sr.RequestError:
                if debug: print(_red + f"Audio recognition error" + _white)
def Start():
    """Initial loop"""
    global markerColor, playerColor, AIColor, RC, virtualBoard, debug, boardCoords
    command = GetInput("str", "Select action: \n")
    if command == "Test ROB":
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
    elif command == "Setup":
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
        #Set real board to current board state
        Main()
    else:
        if virtualBoard != prevBoard:
            RC.Emote("no", debug=debug)
            for movement in RC.MoveToBoard(prevBoard, virtualBoard, debug):
                RC.MoveRobot(movement, debug=debug)
            Main()
        if virtualBoard.turn == 1:
            if virtualBoard.IsCheckmate(debug) or virtualBoard.IsStalemate(20, debug=debug):
                virtualBoard.turn = 0
                Main()
            RC.Emote()
            #Detect player input and validate it
            voiceInput = False
            while voiceInput == False:
                voiceInput = FindVoiceInput(["turn, finished, done, ready"], debug=debug)
            currentBoard.board = ReadBoard(RC.MoveAndCapture(debug=debug), playerColor, AIColor, boardCoords, debug=debug)
            movement = virtualBoard.FindMovement(currentBoard, debug)
            #Either perform the movement inside the script or undo it and repeat turn
            currentBoard.board = ReadBoard(RC.MoveAndCapture(debug=debug), playerColor, AIColor, boardCoords, debug=debug)
            for i, j in [(x, y) for x in range(0, virtualBoard.height) for y in range(0, virtualBoard.height)]:
                j += 1
                if virtualBoard.board[i][j] == currentBoard.board[i][j]:
                    continue
                else:
                    RC.Emote("no", debug=debug)
                    for movement in RC.MoveToBoard(currentBoard, virtualBoard, debug):
                        RC.MoveRobot(movement, debug=debug)
                    Main()
            RC.Emote("yes", debug=debug)
            inputPos = GetInput("list", "Which tile do you want to move? <[↓, →]> \n")
            if not virtualBoard.InsideBounds(inputPos, debug=debug):
                input(_yellow + "Invalid selection, press enter to try again" + _white)
                print(virtualBoard)
                Main() 
            inputPos = Tile(inputPos[0], inputPos[1])
            posMoves = virtualBoard.PossibleMovements(inputPos, debug)
            if len(posMoves[1]) == 0:
                input(_yellow + "Invalid selection, press enter to try again" + _white)
                print(virtualBoard)
                Main() 
            print(posMoves[0])
            inputTarget = GetInput("int", "Which movement do you want to make? <Number> \n")
            inputTarget -= 1
            if inputTarget not in range(len(posMoves[1])):
                input(_yellow + "Invalid selection, press enter to try again" + _white)
                print(virtualBoard)
                Main()
            movement = posMoves[1][inputTarget] 
            if virtualBoard.ValidateMovement(movement, debug):
                virtualBoard.MoveTile(movement, debug=debug)
                virtualBoard.ChangeTurn(debug)
                print(virtualBoard)
                Main() 
            else:
                input(_yellow + "Internal error, press enter to try again" + _white)
                print(virtualBoard)
                Main() 
        else:
            if virtualBoard.IsCheckmate(debug) or virtualBoard.IsStalemate(debug=debug):
                print("Game has ended, the player wins")
                virtualBoard.turn = 0
                Main()
            movement = MiniMax(virtualBoard, debug=debug)
            movement3D = RC.Movement2Dto3D(movement, debug)
            RC.MoveRobot(movement3D, debug=debug)
            virtualBoard.MoveTile(movement[0], debug=debug)
            currentBoard.board = ReadBoard(RC.MoveAndCapture(debug=debug), playerColor, AIColor, boardCoords, debug=debug)
            for i, j in [(x, y) for x in range(0, virtualBoard.height) for y in range(0, virtualBoard.height)]:
                j += 1
                if virtualBoard.board[i][j] == currentBoard.board[i][j]:
                    continue
                else:
                    RC.Emote("no", debug=debug)
                    virtualBoard.MoveTile(movement[0].Reversed(), debug=debug)
                    for movement in RC.MoveToBoard(currentBoard, virtualBoard, debug):
                        RC.MoveRobot(movement, debug=debug)
                    Main()
            RC.Emote("yes", debug=debug)
            for movement in RC.MoveToBoard(currentBoard, virtualBoard, debug):
                RC.MoveRobot(movement, debug=debug)
            RC.MoveToBoard(currentBoard, virtualBoard)
            virtualBoard.ChangeTurn(debug)
            print(virtualBoard)
            Main()
Start()