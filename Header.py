import sys
if not sys.hexversion > 0x03000000:
    version = 2
else:
    version = 3


if version == 2:
    from Tkinter import *
    from tkFileDialog import asksaveasfilename
if version == 3:
    from tkinter import *
    from tkinter.filedialog import asksaveasfilename
import threading
import socket
import random
import math
import pygubu
import pathlib
import sqlite3

strProgramName = "lanchat"
commands = ["nick", "connect", "disconnect", "host"]
conn_array = []  # stores open sockets
secret_array = dict()  # key: the open sockets in conn_array,
# value: integers for encryption
username_array = dict()  # key: the open sockets in conn_array,

username = "Self"

location = 0
port = 0
top = ""

is_hinted = False

main_body_text = 0

if len(sys.argv) > 1 and sys.argv[1] == "-cli":
    print("Starting command line chat")
    isCLI = True
else:
    isCLI = False
