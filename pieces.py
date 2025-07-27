from abc import ABC, abstractmethod
black_list = ['10', '20', '30', '40', '50', '60']
white_list = ['1', '2', '3', '4', '5', '6']
def convert_to_word(num_name) -> str:
    convert_dictionary = {
            '1': 'white pawn',
            '2': 'white bishop',
            '3': 'white knight',
            '4': 'white rook',
            '5': 'white queen',
            '6': 'white king',
            '10': 'black pawn',
            '20': 'black bishop',
            '30': 'black knight',
            '40': 'black rook',
            '50': 'black queen',
            '60': 'black king',
            '0': 'empty'
    }
    return convert_dictionary[num_name]
    
class Board:
    
    def __init__(self):
        self.board:list = [['0' for _ in range(8)] for _ in range(8)]
        self.obj_board = [['0' for _ in range(8)] for _ in range(8)]
        self.last_move = {'piece': None, 'from': None, 'to': None}
        
    def print_board(self):
        for row in reversed(self.board):
            for cell_indx, cell in enumerate(row):
                if cell_indx == 7:
                    print(cell.rjust(2))
                else:
                    print(cell.rjust(2), end='|')
    
    def is_in_check(self, player) -> bool:
        enemy_pieces : list = []
        for row in self.obj_board:
            for enemy_piece in row:
                if enemy_piece != '0' and enemy_piece.color != player.color:
                    enemy_pieces.append(enemy_piece)


        return player.king.is_in_check(enemy_pieces)

class AbstractPiece(ABC):
    def __init__(self, x, y, board:Board, player, color:str):
        self.place:dict = {'x':x - 1, 'y':y - 1}
        self.board = board
        self.color = color
        self.player = player
        self.board.board[self.place['y']][self.place['x']] = self.name
        self.board.obj_board[self.place['y']][self.place['x']] = self

    def __str__(self) -> str:
        return convert_to_word(self.name)
      
    def move_to(self, new_x:int, new_y:int) -> None:
        
        captured_piece = self.board.obj_board[new_y - 1][new_x - 1]
        if captured_piece != '0':
            captured_piece.remove_piece(True)

        self.remove_piece(False)

        self.place['x'] = new_x - 1
        self.place['y'] = new_y - 1
        
        self.board.board[self.place['y']][self.place['x']] = self.name
        self.board.obj_board[self.place['y']][self.place['x']] = self
    
        if isinstance(self, Pawn) and (self.place['y'] == 0 or self.place['y'] == 7):
            self.promote()
        
    def remove_piece(self, kill) -> None:
        self.board.board[self.place['y']][self.place['x']] = '0'
        self.board.obj_board[self.place['y']][self.place['x']] = '0'
        if kill is True:  
            self.player.pieces.remove(self)
            
    @abstractmethod
    def check_for_pieces_in_the_way(self, start:list, end:list) -> bool:
        pass
    
    @abstractmethod
    def is_valid_move(self, piece_place:list, piece_move:list, player_color) -> bool:
        if player_color == self.color and piece_place != piece_move:
            return self.dont_eat_your_own_piece(piece_move)
        return False
    
    def dont_eat_your_own_piece(self, piece_move:list) -> bool:
        if self.color == 'white':
            if int(self.board.board[piece_move[1] - 1][piece_move[0] - 1]) % 10 == 0:
                return True
            return False
        else:
            if int(self.board.board[piece_move[1] - 1][piece_move[0] - 1]) % 10 != 0 or self.board.board[piece_move[1] - 1][piece_move[0] - 1] == '0':
                return True
            return False
    
class Pawn(AbstractPiece):
    def __init__(self, x, y, board, player, color):
        self.name = '1' if color == 'white' else '10'
        super().__init__(x, y, board, player, color)
    
    def check_for_pieces_in_the_way(self) -> bool:
        pass
    
    def is_valid_move(self, piece_place, piece_move, player_color):
        if super().is_valid_move(piece_place, piece_move, player_color):
            start_position = 1 if self.color == 'white' else 6
            direction = 1 if self.color == 'white' else -1

            if piece_place[0] == piece_move[0]:  # Moving straight
                if self.board.board[piece_move[1] - 1][piece_move[0] - 1] == '0':
                    if piece_move[1] - piece_place[1] == direction:
                        return True
                    elif piece_move[1] - piece_place[1] == 2 * direction and piece_place[1] - 1 == start_position:
                        if self.board.board[piece_move[1] - direction - 1][piece_move[0] - 1] == '0':
                            return True  # Initial double move

            elif abs(piece_move[0] - piece_place[0]) == 1 and piece_move[1] - piece_place[1] == direction:
                target_square = self.board.board[piece_move[1] - 1][piece_move[0] - 1]

                if target_square != '0':
                    return self.dont_eat_your_own_piece(piece_move)  # Normal diagonal capture

                elif self.en_passant(piece_place, piece_move):
                    return True  # En passant capture

        return False

        
    def promote(self) -> None:
        while True:
            promotion_choice = input("Promote your pawn to (Q)ueen, (R)ook, (B)ishop, or (K)nignt: ").lower()
            if promotion_choice in ['q', 'r', 'b', 'k']:
                if promotion_choice == 'q':
                    Queen(self.place['x'] + 1, self.place['y'] + 1, self.board, self.player, self.color)
                elif promotion_choice == 'r':
                    Rook(self.place['x'] + 1, self.place['y'] + 1, self.board, self.player, self.color)
                elif promotion_choice == 'b':
                    Bishop(self.place['x'] + 1, self.place['y'] + 1, self.board, self.player, self.color)
                elif promotion_choice == 'k':
                    Knight(self.place['x'] + 1, self.place['y'] + 1, self.board, self.player, self.color)
                break
            else:
                print("Invalid choice. Please choose again.")      
    
    def en_passant(self, piece_place: list, piece_move: list) -> bool:
        direction = 1 if self.color == 'white' else -1
        row = 5 if self.color == 'white' else 4  # y=6 (index 5) for white, y=3 (index 4) for black
        # Your pawn must be on the correct row
        if piece_place[1] != row:
            return False
        # Move must be diagonal, 1 forward, 1 sideways
        if not (piece_move[1] - piece_place[1] == direction and abs(piece_move[0] - piece_place[0]) == 1):
            return False
        # Get the expected opponent pawn name
        expected = '1' if self.color == 'black' else '10'

        # Get last move info
        last = self.board.last_move
        if last['piece'] != expected:
            return False
        # Opponent must have moved a pawn 2 steps from its starting row
        if abs(last['to'][1] - last['from'][1]) != 2:
            return False
        # Opponent's final position must be adjacent to your pawn
        if last['to'][1] != piece_place[1]:
            return False  # must be same row as your pawn
        if last['to'][0] != piece_move[0]:
            return False  # must be in the column you're moving into
        # Remove the opponent's pawn from the correct square
        self.board.obj_board[piece_place[1] - 1][piece_move[0] - 1] = '0'
        self.board.board[piece_place[1] - 1][piece_move[0] - 1] = '0'

        return True


class Knight(AbstractPiece):
    def __init__(self, x, y, board, player, color):        
        self.name = '3' if color == 'white' else '30'
        super().__init__(x, y, board, player, color)
        
    def check_for_pieces_in_the_way(self) -> None:
        pass
    
    def is_valid_move(self, piece_place, piece_move, player_color):
        if super().is_valid_move(piece_place, piece_move, player_color):
            # Check for L-shaped moves
            dx = abs(piece_move[0] - piece_place[0])
            dy = abs(piece_move[1] - piece_place[1])
            if (dx == 2 and dy == 1) or (dx == 1 and dy == 2):
                return True
            
        return False

class Rook(AbstractPiece):
    def __init__(self, x, y, board, player, color, short_or_long_castle):
        self.name = '4' if color == 'white' else '40'
        self.castle = short_or_long_castle
        self.rook_has_moved = False
        super().__init__(x, y, board, player, color)
        
    def check_for_pieces_in_the_way(self, start: list, end: list) -> bool:
        x1, y1 = start
        x2, y2 = end

        if y1 == y2:
            # Horizontal movement
            step = 1 if x2 > x1 else -1
            for x in range(x1 + step, x2, step):
                if self.board.obj_board[y1 - 1][x - 1] != '0':
                    return False

        elif x1 == x2:
            # Vertical movement
            step = 1 if y2 > y1 else -1
            for y in range(y1 + step, y2, step):
                if self.board.obj_board[y - 1][x1 - 1] != '0':
                    return False

        self.rook_has_moved = True
        return True


    def is_valid_move(self, piece_place, piece_move, player_color):
        if player_color == self.color and piece_place != piece_move:
            if self.dont_eat_your_own_piece(piece_move):
            
                if piece_place[0] == piece_move[0] or piece_place[1] == piece_move[1]:
                    # Check if there are pieces in the way
                    return self.check_for_pieces_in_the_way(piece_place, piece_move)
                
        return False

class Bishop(AbstractPiece):
    def __init__(self, x, y, board, player, color):
        self.name = '2' if color == 'white' else '20'
        super().__init__(x, y, board, player, color)
        
    def check_for_pieces_in_the_way(self, start, end) -> bool:
        x1, y1 = start
        x2, y2 = end

        dx = 1 if x2 > x1 else -1
        dy = 1 if y2 > y1 else -1

        x, y = x1 + dx, y1 + dy
        while x != x2 and y != y2:
            if self.board.board[y - 1][x - 1] != '0':
                return False
            x += dx
            y += dy

        return True
    
    def is_valid_move(self, piece_place, piece_move, player_color):
        if player_color == self.color and piece_place != piece_move:
            if self.dont_eat_your_own_piece(piece_move):
                x1, y1 = piece_place
                x2, y2 = piece_move

                # Check for diagonal movement
                if abs(x2 - x1) == abs(y2 - y1):
                    # Check for clear path
                    return self.check_for_pieces_in_the_way(piece_place, piece_move)
            
        return False
    
class Queen(AbstractPiece):
    def __init__(self, x, y, board, player, color):
        self.name = '5' if color == 'white' else '50'
        super().__init__(x, y, board, player, color)
    
    def check_for_pieces_in_the_way(self, piece_place:list, piece_move:list) -> bool:
        return Bishop.check_for_pieces_in_the_way(self, piece_place, piece_move) or Rook.check_for_pieces_in_the_way(self, piece_place, piece_move)
        
    
    def is_valid_move(self, piece_place, piece_move, player_color):
        if player_color != self.color or piece_place == piece_move:
            return False

        if not self.dont_eat_your_own_piece(piece_move):
            return False

        x1, y1 = piece_place
        x2, y2 = piece_move

        dx = abs(x2 - x1)
        dy = abs(y2 - y1)

        # Diagonal move (Bishop-style)
        if dx == dy:
            return self.check_diagonal_clear(piece_place, piece_move)

        # Straight move (Rook-style)
        if x1 == x2 or y1 == y2:
            return self.check_straight_clear(piece_place, piece_move)

        return False
    def check_straight_clear(self, start, end):
        x1, y1 = start
        x2, y2 = end

        if x1 == x2:
            step = 1 if y2 > y1 else -1
            for y in range(y1 + step, y2, step):
                if self.board.obj_board[y - 1][x1 - 1] != '0':
                    return False
        elif y1 == y2:
            step = 1 if x2 > x1 else -1
            for x in range(x1 + step, x2, step):
                if self.board.obj_board[y1 - 1][x - 1] != '0':
                    return False

        return True

    def check_diagonal_clear(self, start, end):
        x1, y1 = start
        x2, y2 = end

        dx = 1 if x2 > x1 else -1
        dy = 1 if y2 > y1 else -1

        x, y = x1 + dx, y1 + dy
        while x != x2 and y != y2:
            if self.board.obj_board[y - 1][x - 1] != '0':
                return False
            x += dx
            y += dy

        return True


class King(AbstractPiece):
    def __init__(self, x, y, board, player, color):
        self.name = '6' if color == 'white' else '60'
        self.king_has_moved = False
        super().__init__(x, y, board, player, color)

    def check_for_pieces_in_the_way() -> None:
        pass
    
    def is_in_check(self, enemy_pieces: tuple[AbstractPiece, ...]) -> bool:
        
        return any(piece.is_valid_move([piece.place['x'], piece.place['y']], [self.place['x'], self.place['y']], piece.color) for piece in enemy_pieces)


    def castle(self, rook:Rook) -> bool:
        
        if self.king_has_moved or rook.rook_has_moved:
            print('You cannot castle, the king or this rook has already moved')
            return False
        
        self.x = self.place['x']
        self.y = self.place['y']
        
        if rook.castle == 'short':
            if self.board.board[self.y][self.x + 1] == '0' and\
            self.board.board[self.y][self.x + 2] == '0' and\
            rook.rook_has_moved == False:
                self.move_to(self.x + 3, self.y + 1)
                rook.move_to(self.x + 2, self.y + 1)
                return True

        elif rook.castle == 'long':
            if self.board.board[self.y][self.x - 1] == '0' and\
            self.board.board[self.y][self.x - 2] == '0' and\
            self.board.board[self.y][self.x - 3] == '0' and\
            rook.rook_has_moved == False:
                self.move_to(self.x - 1, self.y + 1)
                rook.move_to(rook.place['x'] + 4, self.y + 1)
                return True

        return False

    def is_valid_move(self, piece_place, piece_move, player_color):
        if super().is_valid_move(piece_place, piece_move, player_color):
            if abs(piece_move[0] - piece_place[0]) <= 1 and abs(piece_move[1] - piece_place[1]) <= 1:
                if self.dont_eat_your_own_piece(piece_move):
                    self.king_has_moved = True
                    return True

        return False