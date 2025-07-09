class Piece:
    def __init__(self, name, color):
        self.name = name
        self.color = color

    def __repr__(self):
        return f"{self.color[0].upper()}{self.name}"


class ChessBoard:
    def __init__(self):
        # Initialize a 8x8 board with starting positions
        self.board = self.create_initial_board()
        self.condition = ""

    def create_initial_board(self):
        board = [[None for _ in range(8)] for _ in range(8)]
        # Place pawns
        for i in range(8):
            board[1][i] = Piece('P', 'black')
            board[6][i] = Piece('P', 'white')
        # Place Rooks
        board[0][0] = board[0][7] = Piece('R', 'black')
        board[7][0] = board[7][7] = Piece('R', 'white')
        # Place Knights
        board[0][1] = board[0][6] = Piece('N', 'black')
        board[7][1] = board[7][6] = Piece('N', 'white')
        # Place Bishops
        board[0][2] = board[0][5] = Piece('B', 'black')
        board[7][2] = board[7][5] = Piece('B', 'white')
        # Place Queens
        board[0][3] = Piece('Q', 'black')
        board[7][3] = Piece('Q', 'white')
        # Place Kings
        board[0][4] = Piece('K', 'black')
        board[7][4] = Piece('K', 'white')
        return board

    def print_board(self):
        print("  a  b  c  d  e  f  g  h")
        for row in range(8):
            print(8 - row, end=' ')
            for col in range(8):
                piece = self.board[row][col]
                if piece is None:
                    print('--', end=' ')
                else:
                    print(piece, end=' ')
            print(8 - row)
        print("  a  b  c  d  e  f  g  h")

    def move_piece(self, start, end, color):
        # Attempts to move piece
        start_row, start_col = self.parse_position(start)
        end_row, end_col = self.parse_position(end)
        piece = self.board[start_row][start_col]

        if piece is None:
            print("No piece at the starting position.")
            return False
        if piece.color != color:
            print(f"It's {color}'s turn.")
            return False
        if not self.is_valid_move(piece, start_row, start_col, end_row, end_col):
            print("Invalid move for that piece.")
            return False

        # Simulate the move
        target_piece = self.board[end_row][end_col]
        self.board[end_row][end_col] = piece
        self.board[start_row][start_col] = None

        # Check if the move leaves the king in check
        if self.is_in_check(color):
            # Undo the move
            self.board[start_row][start_col] = piece
            self.board[end_row][end_col] = target_piece
            print("Move leaves the king in check. Try a different move.")
            return False

        # Move is valid
        print(f"{color.capitalize()} moved {piece.name} from {start} to {end}.")
        
        # Check for checkmate
        opponent_color = 'white' if color == 'black' else 'black'
        if self.is_in_check(opponent_color):
            if self.is_checkmate(opponent_color):
                print(f"Checkmate! {color.capitalize()} wins!")
                return True
            else:
                print(f"Check! {opponent_color.capitalize()} is in check.")
        return True

    def parse_position(self, pos):
        col = ord(pos[0].lower()) - ord('a')
        row = 8 - int(pos[1])
        return row, col

    def is_valid_move(self, piece, start_row, start_col, end_row, end_col):
        # Basic move validation based on piece type
        delta_row = end_row - start_row
        delta_col = end_col - start_col

        target_piece = self.board[end_row][end_col]
        # Cannot capture your own piece
        if target_piece and target_piece.color == piece.color:
            return False
        # Pawn movement
        if piece.name == 'P':
            direction = -1 if piece.color == 'white' else 1
            # Move forward
            if delta_col == 0:
                if delta_row == direction and target_piece is None:
                    return True
                # Two squares from starting position
                if ((piece.color == 'white' and start_row == 6) or
                    (piece.color == 'black' and start_row == 1)) and \
                   delta_row == 2 * direction and target_piece is None and \
                   self.board[start_row + direction][start_col] is None:
                    return True
            # Capture
            if abs(delta_col) == 1 and delta_row == direction and target_piece is not None:
                return True
            return False
        # Rook movement
        elif piece.name == 'R':
            if delta_row != 0 and delta_col != 0:
                return False
            if not self.is_path_clear(start_row, start_col, end_row, end_col):
                return False
            return True
        # Knight movement 
        elif piece.name == 'N':
            if (abs(delta_row), abs(delta_col)) in [(2, 1), (1, 2)]:
                return True
            return False
        # Bishop movement
        elif piece.name == 'B':
            if abs(delta_row) != abs(delta_col):
                return False
            if not self.is_path_clear(start_row, start_col, end_row, end_col):
                return False
            return True
        # Queen movement
        elif piece.name == 'Q':
            if abs(delta_row) == abs(delta_col) or delta_row == 0 or delta_col == 0:
                if not self.is_path_clear(start_row, start_col, end_row, end_col):
                    return False
                return True
            return False
        # King movement
        elif piece.name == 'K':
            if max(abs(delta_row), abs(delta_col)) == 1:
                return True
            return False

        return False

    def is_path_clear(self, start_row, start_col, end_row, end_col):
        step_row = 0
        step_col = 0
        if end_row > start_row:
            step_row = 1
        elif end_row < start_row:
            step_row = -1
        if end_col > start_col:
            step_col = 1
        elif end_col < start_col:
            step_col = -1

        current_row = start_row + step_row
        current_col = start_col + step_col

        while (current_row != end_row) or (current_col != end_col):
            if self.board[current_row][current_col] is not None:
                return False
            current_row += step_row
            current_col += step_col

        return True

    def is_in_check(self, color):
        king_pos = None

        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.name == 'K' and piece.color == color:
                    king_pos = (row, col)
                    break

        if not king_pos:
            return False

        # Check if any opposing piece can attack the king
        for row in range(8):
            for col in range(8):
                attacker = self.board[row][col]
                if attacker and attacker.color != color:
                    if self.is_valid_move(attacker, row, col, king_pos[0], king_pos[1]):
                        return True
        return False

    def is_checkmate(self, color):
        # Looks for checkmate
        if not self.is_in_check(color):
            return False
        
        self.condition = "Checkmate"

        # Check if the player can make any valid move to escape check
        for start_row in range(8):
            for start_col in range(8):
                piece = self.board[start_row][start_col]
                if piece and piece.color == color:
                    for end_row in range(8):
                        for end_col in range(8):
                            if self.is_valid_move(piece, start_row, start_col, end_row, end_col):
                                # Simulate the move
                                temp_piece = self.board[end_row][end_col]
                                self.board[end_row][end_col] = piece
                                self.board[start_row][start_col] = None
                                
                                if not self.is_in_check(color):
                                    # Undo the move
                                    self.board[start_row][start_col] = piece
                                    self.board[end_row][end_col] = temp_piece
                                    return False
                                
                                # Undo the move
                                self.board[start_row][start_col] = piece
                                self.board[end_row][end_col] = temp_piece

        return True

def main():
    board = ChessBoard()
    current_turn = 'white'

    while True:
        board.print_board()
        print(f"{current_turn.capitalize()}'s move")
        move = input("Enter your move (e.g., e2 e4) or 'q' to quit: ")
        if move.lower() == 'q':
            print("Game over.")
            break
        try:
            start, end = move.split()
        except ValueError:
            print("Invalid input format. Please enter moves like 'e2 e4'.")
            continue

        if board.move_piece(start, end, current_turn):
            current_turn = 'black' if current_turn == 'white' else 'white'
        else:
            print("Move failed. Try again.")

if __name__ == "__main__":
    main()
