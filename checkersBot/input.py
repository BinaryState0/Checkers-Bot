import speech_recognition as sr
from re import findall

_red = "\033[31m"
_blue = "\033[34m"
_white = "\033[37m"
_yellow = "\033[33m"
_green = "\033[32m"
_cyan = "\033[96m"

def FindVoiceInput(keywords: list[str], micID: int = 9, lang = "en-US", timeout = 2, attempts = 1, debug = False) -> bool:
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
        for _ in range(attempts):
            if debug: print(_yellow + f"Attempting to recgonize audio" + _white)
            try:
                audio = rec.listen(source, timeout=timeout, phrase_time_limit=timeout)
            except sr.WaitTimeoutError:
                if debug: print(_red + f"Audio detection timeout" + _white)
                continue
            try:
                text = rec.recognize_google(audio, language=lang).lower()
                if debug: print(_yellow + f"Microphone recognized audio '{text}'" + _white)
                for k in keywords:
                    if k in text:
                        if debug: print(_yellow + f"Keyword '{k}' detected succesfully" + _white)
                        return True, k
            except sr.UnknownValueError:
                if debug: print(_yellow + f"Keyword not detected" + _white)
            except sr.RequestError:
                if debug: print(_red + f"Audio recognition error" + _white)

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
    elif type == "vec2":
        inputPos = findall(r'\d+', userInput)
        inputPos = [int(x) for x in inputPos]
        if len(inputPos) != 2:
            input(_yellow + "Invalid input, press enter to try again" + _white)
            return GetInput(type, message)
        inputPos[0] -= 1
        return inputPos
    elif type == "vec3":
        inputPos = findall(r'\d+', userInput)
        inputPos = [int(x) for x in inputPos]
        if len(inputPos) != 3:
            input(_yellow + "Invalid input, press enter to try again" + _white)
            return GetInput(type, message)
        inputPos[0] -= 1
        return inputPos