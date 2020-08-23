'''This file is code I've removed from the program, but might want to reference for inspiration periodically'''

def determine_check(game, msg = None):
    # for piece in the dictionary, check all of its moves for check
    active_pieces = game.active_pieces()
    opponent_king = game.opponent_king()
    opponent_king_space = opponent_king.space

    for piece in active_pieces:
        piece.generate_move_list(game.spaces, piece.max_move, game.en_passant_turn)
        moves = piece.move_list
        if opponent_king_space in moves:
            return True

    return False


class PieceList(arcade.SpriteList):
    def __init__(self):
        super().__init__()
        self.king = None

    def add_king(self, piece):
        self.append(piece)
        self.king = piece


class MoveRecord:
    def __init__(self, game):
        self.space_list = copy.copy(game.space_list)
        self.piece_list = copy.copy(game.piece_list)
        self.player_list = copy.copy(game.player_list)
        self.en_passant_turn = copy.copy(game.en_passant_turn)
        self.active_player = copy.copy(game.active_player)
