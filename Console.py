from Header import *
import Utils


class Console():
    def __init__(self) -> None:
        print("Starting command line chat")
    def mainloop(self):
        while(1):
          p=input()
          print(p)
    def writeToScreen(self, text, username=""):
        """Places text to main text body in format "username: text"."""
        if username:
            print(username + ": " + text)
        else:
            print(text)

    def processUserInput(self, text):
        """ClI version of processUserText."""
        if text[0] != "/":
            Utils.placeText(self, text)
        else:
            if text.find(" ") == -1:
                command = text[1:]
            else:
                command = text[1:text.find(" ")]
            params = text[text.find(" ") + 1:].split(" ")
            Utils.processUserCommands(command, params, self)
