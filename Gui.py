from Header import *
import Utils


class Gui(Tk):
    def __init__(self):
        super().__init__()
        self.title(strProgramName)
        self.mbMain = Menu(self)
        self.frmMain = Frame(self, height=20, width=50)
        self.createMenus()
        self.txtChat = Text(self.frmMain)
        self.scrlbChat = Scrollbar(self.frmMain)
        self.txtChat.focus_set()
        self.scrlbChat.pack(side=RIGHT, fill=Y)
        self.txtChat.pack(side=LEFT, fill=Y)
        self.scrlbChat.config(command=self.txtChat.yview)
        self.txtChat.config(yscrollcommand=self.scrlbChat.set)
        self.frmMain.pack()
        self.txtChat.insert(END, "Welcome to the chat program!")
        self.txtChat.config(state=DISABLED)
        self.entryInput = Entry(self, width=60)
        self.entryInput.bind("<Return>", self.processUserText)
        self.entryInput.bind("<KeyRelease>", self.processUserTextHighlight)
        self.entryInput.pack()
        self.statusConnect = StringVar()
        self.statusConnect.set("Connect")
        clientType = 1
        Radiobutton(self, text="Client", variable=clientType,
                    value=0, command=Utils.toOne).pack(anchor=E)
        Radiobutton(self, text="Server", variable=clientType,
                    value=1, command=Utils.toTwo).pack(anchor=E)
        self.connector = Button(self, textvariable=self.statusConnect,
                           command=lambda: Utils.connects(clientType))
        self.connector.pack()

    def createMenus(self):
        self.createFileMenu()
        self.createConnectionMenu()
        self.createServerMenu()
        self.createHintPopup()
        self.mbMain.add_command(
            label="Contacts", command=lambda: Utils.contacts_window(self))
        self.config(menu=self.mbMain)

    def createFileMenu(self):
        self.mnuFile = Menu(self.mbMain, tearoff=0)
        self.mnuFile.add_command(
            label="Save chat", command=lambda: Utils.saveHistory())
        self.mnuFile.add_command(
            label="Change username", command=lambda: Utils.username_options_window(self))
        self.mnuFile.add_command(label="Exit", command=lambda: self.destroy())
        self.mbMain.add_cascade(label="File", menu=self.mnuFile)

    def createConnectionMenu(self):
        self.mnuConnection = Menu(self.mbMain, tearoff=0)
        self.mnuConnection.add_command(
            label="Quick Connect", command=self.QuickClient)
        self.mnuConnection.add_command(
            label="Connect on port", command=lambda: self.client_options_window())
        self.mnuConnection.add_command(
            label="Disconnect", command=lambda: self.processFlag("-001"))
        self.mbMain.add_cascade(label="Connect", menu=self.mnuConnection)

    def createServerMenu(self):
        self.mnuServer = Menu(self.mbMain, tearoff=0)
        self.mnuServer.add_command(
            label="Launch server", command=lambda:Utils.QuickServer(self))
        self.mnuServer.add_command(label="Listen on port",
                                   command=lambda:Utils.server_options_window(self))
        self.mbMain.add_cascade(label="Server", menu=self.mnuServer)

    def createHintPopup(self):
        self.mnuHint = Menu(self, tearoff=0)
        self.mnuHint.add_command(
            label=commands[0], command=lambda: self.complete(0, commands))
        self.mnuHint.add_command(
            label=commands[1], command=lambda: self.complete(1, commands))
        self.mnuHint.add_command(
            label=commands[2], command=lambda: self.complete(2, commands))
        self.mnuHint.add_command(
            label=commands[3], command=lambda: self.complete(3, commands))

    def complete(self, index, array):
        self.entryInput.insert(1, array[index])

    def showCommandHint(self):
        """When this function invoked a popup will have shown to user
        that contains list of commands
        """
        try:
            self.mnuHint.tk_popup(self.entryInput.winfo_rootx(),
                                  self.entryInput.winfo_rooty())
        finally:
            self.mnuHint.grab_release()

    def processUserTextHighlight(self, event):
        """Takes text from text bar input and highlights entry if it
        begins with '/'.
        """
        global is_hinted
        data = self.entryInput.get()
        if len(data) > 0:
            if data[0] != "/":  # is not a command
                self.entryInput.config(background="#ffffff")
            else:
                self.entryInput.config(background="#ffdfcf")
        else:  # there is no any text
            self.entryInput.config(background="#ffffff")
        if len(data) == 1 and not is_hinted:
            if data[0] == "/":  # is not a command
                self.showCommandHint()
                is_hinted = True
        if len(data) == 0:
            is_hinted = False

    def processUserText(self, event):
        """Takes text from text bar input and calls processUserCommands if it
        begins with '/'.
        """
        data = self.entryInput.get()
        if data[0] != "/":  # is not a command
            Utils.placeText(self,data)
        else:
            if data.find(" ") == -1:
                command = data[1:]
            else:
                command = data[1:data.find(" ")]
            params = data[data.find(" ") + 1:].split(" ")
            Utils.processUserCommands(command, params, self)
        self.entryInput.delete(0, END)
    
    def writeToScreen(self,text, username=""):
        """Places text to main text body in format "username: text"."""
        self.txtChat.config(state=NORMAL)
        self.txtChat.insert(END, '\n')
        if username:
            self.txtChat.insert(END, username + ": ")
        self.txtChat.insert(END, text)
        self.txtChat.yview(END)
        self.txtChat.config(state=DISABLED)

    def QuickClient(self):
        """Menu window for connection options."""
        window = Toplevel(self)
        window.title("Connection options")
        window.grab_set()
        Label(window, text="Server IP:").grid(row=0)
        destination = Entry(window)
        destination.grid(row=0, column=1)
        go = Button(window, text="Connect", command=lambda:
                    Utils.client_options_go(destination.get(), "9999", window,self))
        go.grid(row=1, column=1)
    
    def client_options_window(self):
        """Launches client options window for getting destination hostname
        and port.
        """
        top = Toplevel(self)
        top.title("Connection options")
        top.protocol("WM_DELETE_WINDOW", lambda: Utils.optionDelete(top))
        top.grab_set()
        Label(top, text="Server IP:").grid(row=0)
        location = Entry(top)
        location.grid(row=0, column=1)
        location.focus_set()
        Label(top, text="Port:").grid(row=1)
        port = Entry(top)
        port.grid(row=1, column=1)
        go = Button(top, text="Connect", command=lambda:
                    Utils.client_options_go(location.get(), port.get(), top,self))
        go.grid(row=2, column=1)
    def optionDelete(self,window):
        self.connector.config(state=NORMAL)
        window.destroy()
    def server_options_window(self):
        """Launches server options window for getting port."""
        top = Toplevel(self)
        top.title("Connection options")
        top.grab_set()
        top.protocol("WM_DELETE_WINDOW", lambda: self.optionDelete(top))
        Label(top, text="Port:").grid(row=0)
        port = Entry(top)
        port.grid(row=0, column=1)
        port.focus_set()
        go = Button(top, text="Launch", command=lambda:
                    Utils.server_options_go(port.get(), top))
        go.grid(row=1, column=1)
    def connects(self,clientType):
        global conn_array
        self.connector.config(state=DISABLED)
        if len(conn_array) == 0:
            if clientType == 0:
                self.client_options_window()
            if clientType == 1:
                self.server_options_window()
        else:
            # connector.config(state=NORMAL)
            for connection in conn_array:
                connection.send("-001".encode())
            self.processFlag("-001")
    def processFlag(self,number, conn=None):
        """Process the flag corresponding to number, using open socket conn
        if necessary.
        """
        global statusConnect
        global conn_array
        global secret_array
        global username_array
        global contact_array
        global isCLI
        t = int(number[1:])
        if t == 1:  # disconnect
            # in the event of single connection being left or if we're just a
            # client
            if len(conn_array) == 1:
                self.writeToScreen("Connection closed.", "System")
                dump = secret_array.pop(conn_array[0])
                dump = conn_array.pop()
                try:
                    dump.close()
                except socket.error:
                    print("Issue with someone being bad about disconnecting")
                if not isCLI:
                    self.statusConnect.set("Connect")
                    self.connector.config(state=NORMAL)
                return

            if conn != None:
                self.writeToScreen("Connect to " + conn.getsockname()
                              [0] + " closed.", "System")
                dump = secret_array.pop(conn)
                conn_array.remove(conn)
                conn.close()

        if t == 2:  # username change
            name = Utils.netCatch(self,conn, secret_array[conn])
            if(Utils.isUsernameFree(name)):
                self.writeToScreen(
                    "User " + username_array[conn] + " has changed their username to " + name, "System")
                username_array[conn] = name
                contact_array[
                    conn.getpeername()[0]] = [conn.getpeername()[1], name]
    def Runner(self,conn, secret):
        global username_array
        while 1:
            data = Utils.netCatch(self,conn, secret)
            if data != 1:
                self.writeToScreen(data, username_array[conn])
