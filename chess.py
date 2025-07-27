import pieces as p

algebraic_notation_row = {'a':1, 'b':2, 'c':3, 'd':4, 'e':5, 'f':6, 'g':7, 'h':8}

class Player:    
    def __init__(self, color, board:p.Board):
        self.color = color
        # Set starting row based on color
        self.board = board
        
        if self.color == 'white':
            main_row, pawn_row = 1, 2
        else:
            main_row, pawn_row = 8, 7

        self.king = p.King(5, main_row, board, self, self.color)
        self.pieces = [
            p.Queen(4, main_row, board, self, self.color),
            self.king,
            p.Rook(1, main_row, board, self, self.color, 'long'),
            p.Rook(8, main_row, board, self, self.color, 'short'),
            p.Bishop(3, main_row, board, self, self.color),
            p.Bishop(6, main_row, board, self, self.color),
            p.Knight(2, main_row, board, self, self.color),
            p.Knight(7, main_row, board, self, self.color)
        ]
        self.pieces += [p.Pawn(i, pawn_row, board, self, self.color) for i in range(1, 9)]
        
    def convert_algebraic_notation(self, algebraic_notation) -> list:
        try:
            if len(algebraic_notation) == 2 and 0 < int(algebraic_notation[1]) < 9 and algebraic_notation[0] in algebraic_notation_row.keys():
                return list([algebraic_notation_row[algebraic_notation[0]], int(algebraic_notation[1])])
        
        except (KeyError, ValueError):
            pass
        
        return False
    
    def from_where_to_move(self) -> list:
        while True:
            print(self.color.capitalize() + "'s turn")
            place_as_input = input("Please enter your piece's location in algebraic notation: ")
            clean_place = self.convert_algebraic_notation(place_as_input)
            if clean_place != False:
                piece = self.board.obj_board[clean_place[1] - 1][clean_place[0] - 1]
                if piece != '0':
                    break
                else:
                    print('There is no piece there')
            else:
                print("That is not a valid location...")
    
        return [clean_place ,piece]
            
    def where_to_move(self) -> list: 
        while True:
            move_as_input = input('Please enter your move in algebraic notation: ')
            if move_as_input.lower() in ['o-o', 'o-o-o']:
                clean_move = move_as_input.lower()
                break  
            clean_move = self.convert_algebraic_notation(move_as_input)
            if clean_move != False:
                break
            else:
                print('That is not a valid notation...')
        return clean_move
    
class Game:
    def __init__(self, players:tuple, board):
        self.players : tuple = players
        self.game_board:p.Board = board

    def main_game(self):
        game_over = False
        while True:
            for player in self.players:
                self.game_board.print_board()
                self.take_movement_input(player)
                if self.win_lose():
                    game_over = True
                    self.game_board.print_board()
                    break
            if game_over:
                break
        print('Game Over, well played!')
        exit()
        
    def win_lose(self) -> bool:
        white, black = self.players
        if white.king in white.pieces and black.king in black.pieces:
            print('all good')
            return False
        elif white.king in white.pieces:
            print('White wins!')
            return True
        elif black.king in black.pieces:
            print('Black wins!')
            return True
        print('Already checked')

    def take_movement_input(self, player:Player) -> None:
        place = player.from_where_to_move()
        piece:p.AbstractPiece = place[-1]
        move = player.where_to_move()

        if move == 'o-o':
            rook = player.pieces[3]
            castling = player.pieces[1].castle(rook)
            if not castling:
                self.take_movement_input(player)
                
            return
        
        elif move == 'o-o-o':
            rook = player.pieces[2]
            castling = player.pieces[1].castle(rook)
            if not castling:
                self.take_movement_input(player)
            
            return
            
        print(f"Place: {place[0]} Move: {move[0]}, {move[1]}")
        valid_or_no = piece.is_valid_move([place[0][0], place[0][1]], [move[0], move[1]], player.color)
        if valid_or_no == False:
            print('That was not a valid input...')
            self.take_movement_input(player)
        else:
            self.game_board.last_move = {
                'piece': piece.name,
                'from': place[0],
                'to': [move[0], move[1]]
            }
            piece.move_to(move[0], move[1])
            
            other_player = self.players[0] if self.players[1] == player else self.players[1]
            if self.game_board.is_in_check(other_player):
                print(f'**The {other_player.color} king is in check!**')


game_board = p.Board()

white = Player('white', game_board)
black = Player('black', game_board)

game = Game((white, black), game_board)
game.main_game()
