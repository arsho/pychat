from Header import *
# So,
#  x_encode your message with the key, then pass that to
#  refract to get a string out of it.
# To decrypt, pass the message back to x_encode, and then back to refract


def binWord(word):
    """Converts the string into binary."""
    master = ""
    for letter in word:
        temp = bin(ord(letter))[2:]
        while len(temp) < 7:
            temp = '0' + temp
        master = master + temp
    return master


def xcrypt(message, key):
    """Encrypts the binary message by the binary key."""
    count = 0
    master = ""
    for letter in message:
        if count == len(key):
            count = 0
        master += str(int(letter) ^ int(key[count]))
        count += 1
    return master


def x_encode(string, number):
    """Encrypts the string by the number."""
    return xcrypt(binWord(string), bin(number)[2:])


def refract(binary):
    """Returns the string representation of the binary.
    Has trouble with spaces.

    """
    master = ""
    for x in range(0, int(len(binary) / 7)):
        master += chr(int(binary[x * 7: (x + 1) * 7], 2) + 0)
    return master


def formatNumber(number):
    """Ensures that number is at least length 4 by
    adding extra 0s to the front.

    """
    temp = str(number)
    while len(temp) < 4:
        temp = '0' + temp
    return temp


def netThrow(parent,conn, secret, message):
    """Sends message through the open socket conn with the encryption key
    secret. Sends the length of the incoming message, then sends the actual
    message.

    """
    try:
        conn.send(formatNumber(len(x_encode(message, secret))).encode())
        conn.send(x_encode(message, secret).encode())
    except socket.error:
        if len(conn_array) != 0:
            parent.writeToScreen(
                "Connection issue. Sending message failed.", "System")
            parent.processFlag("-001")


def netCatch(parent,conn, secret):
    """Receive and return the message through open socket conn, decrypting
    using key secret. If the message length begins with - instead of a number,
    process as a flag and return 1.

    """
    try:
        data = conn.recv(4)
        if data.decode()[0] == '-':
            parent.processFlag(data.decode(), conn)
            return 1
        data = conn.recv(int(data.decode()))
        return refract(xcrypt(data.decode(), bin(secret)[2:]))
    except socket.error:
        if len(conn_array) != 0:
            parent.writeToScreen(
                "Connection issue. Receiving message failed.", "System")
        parent.processFlag("-001")


def isPrime(number):
    """Checks to see if a number is prime."""
    x = 1
    if number == 2 or number == 3:
        return True
    while x < math.sqrt(number):
        x += 1
        if number % x == 0:
            return False
    return True



    # passing a friend who this should connect to (I am assuming it will be
    # running on the same port as the other session)
    if t == 4:
        data = conn.recv(4)
        data = conn.recv(int(data.decode()))
        Client(data.decode(),
               int(contact_array[conn.getpeername()[0]][0])).start()


def processUserCommands(command, param ,parent):
    """Processes commands passed in via the / text input."""
    global conn_array
    global secret_array
    global username
    if command == "nick":  # change nickname
        for letter in param[0]:
            if letter == " " or letter == "\n":
                error_window(parent, "Invalid username. No spaces allowed.")
                return
        if isUsernameFree(param[0]):
            parent.writeToScreen("Username is being changed to " + param[0], "System")
            for conn in conn_array:
                conn.send("-002".encode())
                netThrow(parent,conn, secret_array[conn], param[0])
            username = param[0]
        else:
            parent.writeToScreen(param[0] +
                          " is already taken as a username", "System")
    if command == "disconnect":  # disconnects from current connection
        for conn in conn_array:
            conn.send("-001".encode())
        parent.processFlag("-001")
    if command == "connect":  # connects to passed in host port
        if(options_sanitation(parent,param[1], param[0])):
            Client(param[0], int(param[1]),parent).start()
    if command == "host":  # starts server on passed in port
        if(options_sanitation(parent,param[0])):
            Server(int(param[0]),parent).start()


def isUsernameFree(name):
    """Checks to see if the username name is free for use."""
    global username_array
    global username
    for conn in username_array:
        if name == username_array[conn] or name == username:
            return False
    return True


def passFriends(conn):
    """Sends conn all of the people currently in conn_array so they can connect
    to them.

    """
    global conn_array
    for connection in conn_array:
        if conn != connection:
            conn.send("-004".encode())
            conn.send(
                formatNumber(len(connection.getpeername()[0])).encode())  # pass the ip address
            conn.send(connection.getpeername()[0].encode())
            # conn.send(formatNumber(len(connection.getpeername()[1])).encode()) #pass the port number
            # conn.send(connection.getpeername()[1].encode())

# --------------------------------------------------------------------------



def client_options_go(dest, port, window,parent):
    "Processes the options entered by the user in the client options window."""
    if options_sanitation(parent,port, dest):
        if not isCLI:
            window.destroy()
        Client(dest, int(port),parent).start()
    elif isCLI:
        sys.exit(1)


def options_sanitation(parent,por, loc=""):
    """Checks to make sure the port and destination ip are both valid.
    Launches error windows if there are any issues.

    """
    if version == 2:
        por = unicode(por)
    if not por.isdigit():
        error_window(parent, "Please input a port number.")
        return False
    if int(por) < 0 or 65555 < int(por):
        error_window(parent, "Please input a port number between 0 and 65555")
        return False
    if loc != "":
        if not ip_process(loc.split(".")):
            error_window(parent, "Please input a valid ip address.")
            return False
    return True


def ip_process(ipArray):
    """Checks to make sure every section of the ip is a valid number."""
    if len(ipArray) != 4:
        return False
    for ip in ipArray:
        if version == 2:
            ip = unicode(ip)
        if not ip.isdigit():
            return False
        t = int(ip)
        if t < 0 or 255 < t:
            return False
    return True

def username_options_window(master):
    """Launches username options window for setting username."""
    top = Toplevel(master)
    top.title("Username options")
    top.grab_set()
    Label(top, text="Username:").grid(row=0)
    name = Entry(top)
    name.focus_set()
    name.grid(row=0, column=1)
    go = Button(top, text="Change", command=lambda:
                username_options_go(name.get(), top))
    go.grid(row=1, column=1)


def username_options_go(name, window):
    """Processes the options entered by the user in the
    server options window.

    """
    processUserCommands("nick", [name])
    window.destroy()

# -------------------------------------------------------------------------


def error_window(master, texty):
    """Launches a new window to display the message texty."""
    global isCLI
    if isCLI:
        texty.writeToScreen(texty, "System")
    else:
        window = Toplevel(master)
        window.title("ERROR")
        window.grab_set()
        Label(window, text=texty).pack()
        go = Button(window, text="OK", command=window.destroy)
        go.pack()
        go.focus_set()

def load_contacts():
    """Loads the recent chats out of the persistent file contacts.dat."""
    global contact_array
    try:
        filehandle = open("data\\contacts.dat", "r")
    except IOError:
        return
    line = filehandle.readline()
    while len(line) != 0:
        temp = (line.rstrip('\n')).split(" ")  # format: ip, port, name
        contact_array[temp[0]] = temp[1:]
        line = filehandle.readline()
    filehandle.close()


def dump_contacts():
    """Saves the recent chats to the persistent file contacts.dat."""
    global contact_array
    try:
        filehandle = open("data\\contacts.dat", "w")
    except IOError:
        print("Can't dump contacts.")
        return
    for contact in contact_array:
        filehandle.write(
            contact + " " + str(contact_array[contact][0]) + " " +
            contact_array[contact][1] + "\n")
    filehandle.close()

def contacts_connect(parent,item):
    """Establish a connection between two contacts."""
    Client(item[1], int(item[2]),parent).start()

class Server (threading.Thread):
    "A class for a Server instance."""

    def __init__(self, port,parent):
        threading.Thread.__init__(self)
        self.port = port
        self.parent=parent

    def run(self):
        global conn_array
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', self.port))

        if len(conn_array) == 0:
            self.parent.writeToScreen(
                "Socket is good, waiting for connections on port: " +
                str(self.port), "System")
        s.listen(1)
        global conn_init
        conn_init, addr_init = s.accept()
        serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serv.bind(('', 0))  # get a random empty port
        serv.listen(1)

        portVal = str(serv.getsockname()[1])
        if len(portVal) == 5:
            conn_init.send(portVal.encode())
        else:
            conn_init.send(("0" + portVal).encode())

        conn_init.close()
        conn, addr = serv.accept()
        conn_array.append(conn)  # add an array entry for this connection
        self.parent.writeToScreen("Connected by " + str(addr[0]), "System")

        self.parent.statusConnect.set("Disconnect")
        self.parent.connector.config(state=NORMAL)

        # create the numbers for my encryption
        prime = random.randint(1000, 9000)
        while not isPrime(prime):
            prime = random.randint(1000, 9000)
        base = random.randint(20, 100)
        a = random.randint(20, 100)

        # send the numbers (base, prime, A)
        conn.send(formatNumber(len(str(base))).encode())
        conn.send(str(base).encode())

        conn.send(formatNumber(len(str(prime))).encode())
        conn.send(str(prime).encode())

        conn.send(formatNumber(len(str(pow(base, a) % prime))).encode())
        conn.send(str(pow(base, a) % prime).encode())

        # get B
        data = conn.recv(4)
        data = conn.recv(int(data.decode()))
        b = int(data.decode())

        # calculate the encryption key
        global secret_array
        secret = pow(b, a) % prime
        # store the encryption key by the connection
        secret_array[conn] = secret

        conn.send(formatNumber(len(username)).encode())
        conn.send(username.encode())

        data = conn.recv(4)
        data = conn.recv(int(data.decode()))
        if data.decode() != "Self":
            username_array[conn] = data.decode()
            contact_array[str(addr[0])] = [str(self.port), data.decode()]
        else:
            username_array[conn] = addr[0]
            contact_array[str(addr[0])] = [str(self.port), "No_nick"]

        passFriends(conn)
        threading.Thread(target=self.parent.Runner, args=(conn, secret)).start()
        Server(self.port,self.parent).start()


class Client (threading.Thread):
    """A class for a Client instance."""

    def __init__(self, host, port,parent):
        threading.Thread.__init__(self)
        self.port = port
        self.host = host
        self.parent = parent

    def run(self):
        global conn_array
        global secret_array
        conn_init = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn_init.settimeout(5.0)
        try:
            conn_init.connect((self.host, self.port))
        except socket.timeout:
            self.parent.writeToScreen("Timeout issue. Host possible not there.", "System")
            self.parent.connector.config(state=NORMAL)
            raise SystemExit(0)
        except socket.error:
            self.parent.writeToScreen(
                "Connection issue. Host actively refused connection.", "System")
            self.parent.connector.config(state=NORMAL)
            raise SystemExit(0)
        porta = conn_init.recv(5)
        porte = int(porta.decode())
        conn_init.close()
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((self.host, porte))

        self.parent.writeToScreen("Connected to: " + self.host +
                      " on port: " + str(porte), "System")

        self.parent.statusConnect.set("Disconnect")
        self.parent.connector.config(state=NORMAL)

        conn_array.append(conn)
        # get my base, prime, and A values
        data = conn.recv(4)
        data = conn.recv(int(data.decode()))
        base = int(data.decode())
        data = conn.recv(4)
        data = conn.recv(int(data.decode()))
        prime = int(data.decode())
        data = conn.recv(4)
        data = conn.recv(int(data.decode()))
        a = int(data.decode())
        b = random.randint(20, 100)
        # send the B value
        conn.send(formatNumber(len(str(pow(base, b) % prime))).encode())
        conn.send(str(pow(base, b) % prime).encode())
        secret = pow(a, b) % prime
        secret_array[conn] = secret

        conn.send(formatNumber(len(username)).encode())
        conn.send(username.encode())

        data = conn.recv(4)
        data = conn.recv(int(data.decode()))
        if data.decode() != "Self":
            username_array[conn] = data.decode()
            contact_array[
                conn.getpeername()[0]] = [str(self.port), data.decode()]
        else:
            username_array[conn] = self.host
            contact_array[conn.getpeername()[0]] = [str(self.port), "No_nick"]
        threading.Thread(target=self.parent.Runner, args=(conn, secret)).start()
        # Server(self.port).start()
        # ##########################################################################THIS
        # IS GOOD, BUT I CAN'T TEST ON ONE MACHINE


def QuickServer(parent):
    """Quickstarts a server."""
    Server(9999,parent).start()


def saveHistory():
    """Saves history with Tkinter's asksaveasfilename dialog."""
    global main_body_text
    file_name = asksaveasfilename(
        title="Choose save location",
        filetypes=[('Plain text', '*.txt'), ('Any File', '*.*')])
    try:
        filehandle = open(file_name + ".txt", "w")
    except IOError:
        print("Can't save history.")
        return
    contents = main_body_text.get(1.0, END)
    for line in contents:
        filehandle.write(line)
    filehandle.close()


def toOne():
    global clientType
    clientType = 0


def toTwo():
    global clientType
    clientType = 1

def placeText(parent,text):
    """Places the text from the text bar on to the screen and sends it to
    everyone this program is connected to.

    """
    global conn_array
    global secret_array
    global username
    parent.writeToScreen(text, username)
    for person in conn_array:
        netThrow(parent,person, secret_array[person], text)
