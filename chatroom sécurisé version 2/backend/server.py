import threading
import socket
import argparse
import os


class Server(threading.Thread):
    def __init__(self, host, port):
        super().__init__()
        self.connections = []
        self.host = host
        self.port = port
        

    def run(self):

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))

        sock.listen(1)
        print("Listening at", sock.getsockname())


        while True:
            # Accept new connection
            sc, sockname = sock.accept()
            print(f"Nouvelle connexion de {sc.getpeername()}")

            # Create new thread
            server_socket = ServerSocket(sc, sockname, self)

            # Start new thread
            server_socket.start()

            # Add thread to active connections
            self.connections.append(server_socket)
            print("en attente de message(s) de", sc.getpeername())

    def broadcast(self, message, source):
        for connection in self.connections:
            # Send to all connected clients except the source client
            if connection.sockname != source:
                #print("sending message to", connection.sockname)
                connection.send(message)
    
    def remove_connection(self, connection):
        self.connections.remove(connection)
    
class ServerSocket(threading.Thread):
        
    def __init__(self, sc, sockname, server):
        super().__init__()
        self.sc = sc
        self.sockname = sockname
        self.server = server

    def run(self):
        while True:
            message = self.sc.recv(1024).decode("ascii")
            if message:
                print(f"Message recu de {self.sockname}: {message}")
                self.server.broadcast(message, self.sockname)
            else:
                # Client disconnected
                print(f"Client {self.sockname} deconnecte")
                self.sc.close()
                server.remove_connection(self)
                return

    def send(self, message):
        self.sc.sendall(message.encode("ascii"))
    
def exit(server):
    while True:
        ipt = input("")
        if ipt == "stop":
            print("Arret du serveur")
            for connection in server.connections:
                connection.sc.close()

            print("Fermeture du serveur")
            os._exit(0)
            

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Chat Server")
    parser.add_argument("host",  help="IP du serveur")
    parser.add_argument("-p", metavar="PORT", type=int, help="TCP port(default 1060)", default=1060)

    args = parser.parse_args()
    
    server = Server(args.host, args.p)
    server.start()

    exit = threading.Thread(target=exit, args=(server,))
    exit.start()

