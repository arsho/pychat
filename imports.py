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
