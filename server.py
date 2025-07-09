import socket
import threading
from backend import ChessBoard, Piece

class ChessServer:
    def __init__(self, host='localhost', port=5555):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(2)
        self.connections = []
        self.game = ChessBoard()
        self.current_turn = 'white'

    def broadcast(self, message):
        # Send a message to all connected clients
        for client_socket in self.connections:
            client_socket.send(message.encode('utf-8'))

    def handle_client(self, client_socket, player):
        # Handle communication with a single client
        while True:
            if self.game.condition == "Checkmate":
                over_message = f"CHECKMATE"
                self.broadcast(over_message)
                return False

            move = client_socket.recv(1024).decode('utf-8')
            if not move:
                break

            start, end = move.split()

            result = self.game.move_piece(start, end, self.current_turn)

            # Prints board in the server terminal
            self.game.print_board()

            # Updates and sends current turn and the move
            if result:
                self.current_turn = 'black' if self.current_turn == 'white' else 'white'
                move_message = f"MOVE {start} {end}"
                turn_message = f"TURN {self.current_turn}"
                self.broadcast(turn_message)
            else:
                move_message = "INVALID"
            
            self.broadcast(move_message)
                
        # Close the connection for this client
        self.connections.remove(client_socket)
        client_socket.close()

    def start_server(self):
        #Starts the server with the clients
        print("Server is running...")

        while len(self.connections) < 2:
            client_socket, addr = self.server.accept()
            print(f"Player connected from {addr}")
            self.connections.append(client_socket)
            player = 'white' if len(self.connections) == 1 else 'black'
            client_socket.send(f"PLAYER {player}".encode('utf-8'))

            # Start a new thread to handle communication with the client
            threading.Thread(target=self.handle_client, args=(client_socket, player)).start()

# Running the server
if __name__ == "__main__":
    chess_server = ChessServer()
    chess_server.start_server()
