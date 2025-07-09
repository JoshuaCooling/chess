import tkinter as tk
from PIL import Image, ImageTk
import socket
from backend import ChessBoard, Piece
import os
import threading

class ChessClient:
    def __init__(self, root, host='localhost', port=5555):
        self.root = root
        self.root.title("Chess Game")

        # Frame for the Gui
        self.board_frame = tk.Frame(self.root)
        self.board_frame.pack()

        # Frame for messages
        self.message_label = tk.Label(self.root, text="", font=("Arial", 12), bg="lightgray", wraplength=400, justify="center")
        self.message_label.pack(pady=10)

        self.chessboard = ChessBoard()
        self.current_turn = 'white'
        
        self.player = ''
        self.selected_piece = None
        self.start_pos = None

        self.buttons = [[None for _ in range(8)] for _ in range(8)]
        self.piece_images = {}
        self.square_size = 64
        self.load_images()
        self.create_board()

        # Set up the socket to connect to the server
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))
        self.listen_for_server()

    def load_images(self):
        #Loads images for the chess pieces
        pieces = ["P", "R", "N", "B", "Q", "K"]
        for color in ["w", "b"]:
            for piece in pieces:
                image_path = os.path.join(
                    "C:\\Users\\coolj\\OneDrive\\Documents\\Fall24\\datacom\\Project\\images", 
                    f"{color}{piece}.png"
                )
                img = Image.open(image_path)
                img = img.resize((self.square_size, self.square_size), Image.Resampling.LANCZOS)
                self.piece_images[f"{color}{piece}"] = ImageTk.PhotoImage(img)

    def create_board(self):
        # Creates the board
        for row in range(8):
            self.board_frame.rowconfigure(row, weight=1, minsize=self.square_size)
            for col in range(8):
                self.board_frame.columnconfigure(col, weight=1, minsize=self.square_size)
                button = tk.Button(
                    self.board_frame,
                    command=lambda r=row, c=col: self.on_square_click(r, c),
                    bg="green" if (row + col) % 2 == 0 else "brown",
                    padx=0,
                    pady=0,
                    borderwidth=0
                )
                button.grid(row=row, column=col, sticky="nsew")
                self.buttons[row][col] = button

        self.update_board()

    def update_message(self, message):
        #Updates the message in the Gui
        self.message_label.config(text=message)

    def update_board(self):
        # Updates the board with the current state of the game
        for row in range(8):
            for col in range(8):
                piece = self.chessboard.board[row][col]
                bg_color = "green" if (row + col) % 2 == 0 else "brown"
                if piece:
                    image_key = f"{piece.color[0]}{piece.name}"
                    self.buttons[row][col].config(image=self.piece_images.get(image_key, ""), bg=bg_color)
                else:
                    self.buttons[row][col].config(image="", bg=bg_color)


    def on_square_click(self, row, col):
        # Controls clicks on the Gui
        self.update_message("")
        if self.selected_piece is None:
            piece = self.chessboard.board[row][col]
            
            if piece:
                if self.player == self.current_turn:
                    self.selected_piece = piece
                    self.start_pos = (row, col)
                    self.buttons[row][col].config(bg="yellow")
        else:
            start = self.start_pos
            end = (row, col)
            start_pos = self.parse_to_chess_notation(*start)
            end_pos = self.parse_to_chess_notation(row, col)

            # Sends the move to the server
            self.client_socket.send(f"{start_pos} {end_pos}".encode('utf-8'))
            self.selected_piece = None
            self.start_pos = None

    def parse_to_chess_notation(self, row, col):
        # Converts Gui coordinants to chess notation
        col_char = chr(col + ord('a'))
        row_num = 8 - row
        return f"{col_char}{row_num}"

    def listen_for_server(self):
        # Listens for messages from the server
        def receive_messages():
            while True:
                try:
                    message = self.client_socket.recv(1024).decode('utf-8')
                    if message:
                        self.root.after(0, self.process_server_message, message)
                except Exception as e:
                    print(f"Error receiving message: {e}")
                    break

        threading.Thread(target=receive_messages, daemon=True).start()

    def process_server_message(self, message):
        # Processes messages from the server
        if message.startswith("CHECKMATE"):
            self.update_message("Game Over, Checkmate")
        elif message.startswith("PLAYER"):
            _, player = message.split()
            self.player = player
            self.update_message(f"You are playing as {self.player}")
        elif message.startswith("MOVE"):
            _, start_pos, end_pos = message.split()
            self.apply_move(start_pos, end_pos)
        elif message.startswith("TURN"):
            _, turn = message.split()
            self.update_message(f"It is {turn}'s turn")
            self.current_turn = turn
        elif message.startswith("INVALID"):
            if self.current_turn == self.player:
                self.update_message("Invalid move.")
        else:
            print(f"Unexpected message: {message}")

    def apply_move(self, start_pos, end_pos):
        # Convert chess notation to board indices
        start_row, start_col = self.chess_notation_to_index(start_pos)
        end_row, end_col = self.chess_notation_to_index(end_pos)

        # Update the chessboard and the board GUI
        piece = self.chessboard.board[start_row][start_col]
        self.chessboard.board[end_row][end_col] = piece
        self.chessboard.board[start_row][start_col] = None
        
        # After updating the chessboard, update the GUI
        self.update_board()
        
    def chess_notation_to_index(self, pos):
        # Converts chess notation to board coordinates
        col = ord(pos[0]) - ord('a')
        row = 8 - int(pos[1])
        return row, col


# Running the client
if __name__ == "__main__":
    root = tk.Tk()
    ChessClient(root)
    root.mainloop()
