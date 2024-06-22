import socket
import threading
import sys
import os
import tkinter as tk
import argparse

class Send(threading.Thread):
    def __init__(self, sock, name):
        super().__init__()
        self.sock = sock
        self.name = name

    def run(self):
        #Listen for user input and send it to the server

        while True:
            print('{}: '.format(self.name), end='')
            sys.stdout.flush()
            message = sys.stdin.readline()[:-1]

            # Type 'QUIT' to leave the chatroom
            if message == 'QUIT':
                self.sock.sendall('Server: {} a quitté(e) le chat.'.format(self.name).encode('ascii'))
                break

            else:
                self.sock.sendall('{}: {}'.format(self.name, message).encode('ascii'))
            
        print('\nFermeture...')
        self.sock.close()
        os._exit(0)

class Receive(threading.Thread):
    def __init__(self, sock, name):
        super().__init__()
        self.sock = sock
        self.name = name
        self.messages = None

    def run(self):
        # Receive messages from the server
        while True:
            message = self.sock.recv(1024).decode('ascii')
            if message:
                if self.messages:
                    self.messages.insert(tk.END, message)#.decode('ascii'))
                    print('\r{}\n{}: '.format(message, self.name), end = '')#print('\r{}\n{}: '.format(message, self.name), end = '')
                else:
                    print('\r{}\n{}: '.format(message, self.name), end = '')
            
            else:
                # Server has closed
                print('\nLa connexion au server a été perdue\n')
                print('Fermeture...')
                self.sock.close()
                os._exit(0)

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.name = None
        self.messages = None
        
    def start(self):
        # Connect to the server
        print('Tentative de connexion au serveur {}:{}'.format(self.host, self.port))
        self.sock.connect((self.host, self.port))

        print('Connecté au serveur {}:{}'.format(self.host, self.port))

        print()
        self.name = input('Votre nom: ')

        print()
        print('Bienvenue, {}!'.format(self.name))


        send = Send(self.sock, self.name)

        receive = Receive(self.sock, self.name)

        send.start()

        receive.start()

        self.sock.sendall('Server: {} a rejoint le chat. Bienvenue!'.format(self.name).encode('ascii'))

        print("\rTapez 'QUIT' pour quitter")

        print('{}:' .format(self.name), end = '')
        return receive
    
    
    def exit(self, textInput):
        message = textInput.get()
        textInput.delete(0, tk.END)
        self, message.insert(tk.END, '{}:{}' .format(self.name, message))

        # Type 'QUIT' to leave the chatroom
        if message == 'QUIT':
            self.sock.sendall('Server: {} a quitté(e) le chat.'.format(self.name).encode('ascii'))

            print('\nFermeture...')
            self.sock.close()
            os._exit(0)

        # Send message to server for broadcasting
        else:
            self.sock.sendall('{}: {}'.format(self.name, message).encode('ascii'))

def main(host, port):
    #initialize and run GUI application

    client = Client(host, port)
    receive = client.start()

    window = tk.Tk()
    window.title('Chatroom')

    fromMessages = tk.Frame(master=window)
    scrollbar = tk.Scrollbar(master=fromMessages)
    messages = tk.Listbox(master=fromMessages, yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y, expand=False)
    messages.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    client.messages = messages
    receive.messages = messages

    fromMessages.grid(row=0, column=0, columnspan=2, sticky='nsew')
    fromEntry = tk.Frame(master=window)
    textInput = tk.Entry(master=fromEntry)

    textInput.pack(fill=tk.BOTH, expand=True)
    textInput.bind('<Return>', lambda x: client.sent(textInput))
    textInput.insert(0, 'Tapez votre message ici et appuyez sur Entrée pour envoyer')

    btnSend = tk.Button(
        master=window,
        text='Envoyer',
        command=lambda: client.sent(textInput)
    )

    fromEntry.grid(row=1, column=0, padx=10, sticky='ew')
    btnSend.grid(row=1, column=1, pady=10, sticky='ew')

    window.rowconfigure(0, minsize=500 ,weight=1)
    window.rowconfigure(1, minsize=50, weight=0)
    window.columnconfigure(0, minsize=500, weight=1)
    window.columnconfigure(1, minsize=200, weight=0)

    window.mainloop()
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Chat Server")
    parser.add_argument("host",  help="IP du serveur")
    parser.add_argument("-p", metavar="PORT", type=int, help="TCP port(default 1060)", default=1060)

    args = parser.parse_args()

    main(args.host, args.p)
