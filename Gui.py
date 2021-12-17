from pygubu import builder
from Header import *
import Utils


class Gui():
    def __init__(self):
        self.b = builder = pygubu.Builder()
        builder.add_resource_path('resources')
        builder.add_from_file('layouts/lanchat.ui')
        self.wndMain = builder.get_object('mainwindow')
        self.frmMain = builder.get_object('frmMain')
        self.txtChat = builder.get_object('txtChat')
        self.txtChat.config(state=DISABLED)
        self.entryInput = builder.get_object('entryInput')
        self.entryInput.bind("<Return>", self.processUserText)
        self.entryInput.bind("<KeyRelease>", self.processUserTextHighlight)
        self.statusConnect = StringVar()
        self.statusConnect.set("Connect")
        self.mainloop = self.wndMain.mainloop
        self.mnuHint = builder.get_object('mnuHint')
        self.b.connect_callbacks(self)
        self.connector = builder.get_object('connector')
        self.contacts_window()

    def on_mSave(self):
        Utils.saveHistory(self)

    def on_mUsername(self):
        Utils.username_options_window(self)

    def on_mExit(self):
        self.wndMain.destroy()

    def on_mDisconnect(self):
        self.processFlag("-001")

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
            Utils.placeText(self, data)
        else:
            if data.find(" ") == -1:
                command = data[1:]
            else:
                command = data[1:data.find(" ")]
            params = data[data.find(" ") + 1:].split(" ")
            Utils.processUserCommands(command, params, self)
        self.entryInput.delete(0, END)

    def writeToScreen(self, text, username=""):
        """Places text to main text body in format "username: text"."""
        self.txtChat.config(state=NORMAL)
        self.txtChat.insert(END, '\n')
        if username:
            self.txtChat.insert(END, username + ": ")
        self.txtChat.insert(END, text)
        self.txtChat.yview(END)
        self.txtChat.config(state=DISABLED)

    def client_options_window(self):
        """Launches client options window for getting destination hostname
        and port.
        """
        clientOptionWindow(self)

    def server_options_window(self):
        """Launches server options window for getting port."""
        serverOptionWindow(self)

    def connects(self, clientType):
        global conn_array
        self.connector.config(text="disconnected")
        if len(conn_array) == 0:
            if clientType == 0:
                self.client_options_window()
            if clientType == 1:
                self.server_options_window()
        else:
            self.connector.config(text="connected")
            for connection in conn_array:
                connection.send("-001".encode())
            self.processFlag("-001")

    def processFlag(self, number, conn=None):
        """Process the flag corresponding to number, using open socket conn
        if necessary.
        """
        global statusConnect
        global conn_array
        global secret_array
        global username_array

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
                    self.connector.config(text="connected")
                return

            if conn != None:
                self.writeToScreen("Connect to " + conn.getsockname()
                                   [0] + " closed.", "System")
                dump = secret_array.pop(conn)
                conn_array.remove(conn)
                conn.close()

        if t == 2:  # username change
            name = Utils.netCatch(self, conn, secret_array[conn])
            if(Utils.isUsernameFree(name)):
                self.writeToScreen(
                    "User " + username_array[conn] + " has changed their username to " + name, "System")
                username_array[conn] = name
                Utils.contact_array[
                    conn.getpeername()[0]] = [conn.getpeername()[1], name]

    def Runner(self, conn, secret):
        global username_array
        while 1:
            data = Utils.netCatch(self, conn, secret)
            if data != 1:
                self.writeToScreen(data, username_array[conn])

    def contacts_window(self):
        """Displays the contacts window, allowing the user to select a recent
        connection to reuse.
        """
        self.listbox = self.b.get_object('contactListBox')
        print(Utils.contact_array)
        for person in Utils.contact_array:
            self.listbox.insert(END, Utils.contact_array[person][1] + " " +
                                person + " " + Utils.contact_array[person][0])
        self.listbox.pack(side=LEFT, fill=BOTH, expand=1)

    def contacts_remove(self):
        """Remove a contact."""
        item = self.listbox.get(ACTIVE).split(" ")
        if self.listbox.size() != 0:
            self.listbox.delete(ACTIVE)
    
            h = Utils.contact_array.pop(item[1])

    def contacts_add(self):
        """Add a contact."""
        aWindow = Toplevel(self.wndMain)
        aWindow.title("Contact add")
        Label(aWindow, text="Username:").grid(row=0)
        name = Entry(aWindow)
        name.focus_set()
        name.grid(row=0, column=1)
        Label(aWindow, text="IP:").grid(row=1)
        ip = Entry(aWindow)
        ip.grid(row=1, column=1)
        Label(aWindow, text="Port:").grid(row=2)
        port = Entry(aWindow)
        port.grid(row=2, column=1)
        go = Button(aWindow, text="Add", command=lambda:
                    self.contacts_add_helper(name.get(), ip.get(), port.get(),
                                             aWindow, self.listbox))
        go.grid(row=3, column=1)

    def contacts_add_helper(self, username, ip, port, window, listbox):
        """Contact adding helper function. Recognizes invalid usernames and
        adds contact to listbox and Utils.contact_array.
        """
        for letter in username:
            if letter == " " or letter == "\n":
                Utils.error_window(
                    self, "Invalid username. No spaces allowed.")
                return
        if Utils.options_sanitation(self, port, ip):
            listbox.insert(END, username + " " + ip + " " + port)
            Utils.contact_array[ip] = [port, username]
            window.destroy()
            return

class clientOptionWindow():
    def __init__(self,parent) -> None:
        self.parent = parent
        self.b = pygubu.Builder()
        self.b.add_from_file('layouts/clientOption.ui')
        self.top = self.b.get_object('connection_options')
        self.top.protocol("WM_DELETE_WINDOW", lambda: optionDelete(self.top))
        self.top.grab_set()
        self.b.get_object('loc').focus_set()
        self.b.connect_callbacks(self)

    def on_connect(self):
        Utils.client_options_go(
            self.b.get_object('loc').get(), self.b.get_object('port').get(), 
            self.top, self.parent)

class serverOptionWindow():
    def __init__(self,parent):
        self.parent = parent
        self.b = builder.Builder()
        self.b.add_from_file('layouts/serverOption.ui')
        self.top = self.b.get_object('server_options')
        self.top.grab_set()
        self.top.protocol("WM_DELETE_WINDOW", lambda: optionDelete(self.top))
        self.b.connect_callbacks(self)
    def on_launch(self):
        port=self.b.get_object('port').get()
        if Utils.options_sanitation(self.parent, port):
            self.top.destroy()
            Utils.Server(int(port),self.parent).start()

def optionDelete(window):
    window.destroy()
