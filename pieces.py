import arcade
import constants


class Piece(arcade.Sprite):
    def __init__(self, image, player, space, captured):
        self.player = player
        self.captured = captured
        self.original_space = space
        self.space = space
        self.move_list = []
        self.direction_list = []
        self.max_move = constants.BOARD_ROWS
        self.previous_position = None
        self.type = 'Chess piece'

        super().__init__(image, hit_box_algorithm='None')

    def __repr__(self):
        return self.type

    def move_n(self, origin):
        return origin[0], origin[1] + 1

    def move_s(self, origin):
        return origin[0], origin[1]-1

    def move_w(self, origin):
        return origin[0]-1, origin[1]

    def move_e(self, origin):
        return origin[0]+1, origin[1]

    def move_nw(self, origin):
        return origin[0]-1, origin[1]+1

    def move_ne(self, origin):
        return origin[0]+1, origin[1]+1

    def move_se(self, origin):
        return origin[0] + 1, origin[1]-1

    def move_sw(self, origin):
        return origin[0]-1, origin[1]-1

    def move_path(self, origin, spaces, direction, max_move):
        move_list = []
        new_spot = spaces.get(direction(origin))
        while new_spot and len(move_list) < max_move:
            if new_spot.occupant and new_spot.occupant.player == self.player:
                break
            move_list.append(new_spot)
            if new_spot.occupant:
                break
            new_spot = spaces.get(direction(new_spot.space_coord()))
        return move_list

    def generate_move_list(self, spaces, max_move, en_passant_turn):
        origin = self.space.space_coord()
        for direction in self.direction_list:
            self.move_list.extend(self.move_path(origin, spaces, direction, max_move))

    def pickup(self, spaces, en_passant_turn):
        self.previous_position = self.position
        self.generate_move_list(spaces, self.max_move, en_passant_turn)
        for space in self.move_list:
            space.set_temp_color((124, 10, 2))
        self.space.set_temp_color(arcade.color.DARK_GOLDENROD)

    def return_to_previous_position(self):
        self.space.return_original_color()
        self.set_position(self.previous_position[0], self.previous_position[1])

    def got_captured(self, game):
        game.piece_list.remove(self)
        self.captured = True
        self.player.pieces_lost.append(self)

    def move_piece(self, destination, game):
        self.set_position(destination.center_x, destination.center_y)
        self.space.occupant = None  # departing space made empty
        self.space = destination
        destination.occupant = self


class Queen(Piece):
    def __init__(self, player, space, captured=False):
        self.image = "images/white_queen_static.png"
        super().__init__(self.image, player, space, captured)
        self.type = 'Queen'
        self.direction_list = [self.move_n, self.move_s, self.move_w, self.move_e, self.move_nw, self.move_ne,
                               self.move_sw, self.move_se]


class King(Piece):
    def __init__(self, player, space, captured=False):
        self.image = "images/white_king_static.png"
        super().__init__(self.image, player, space, captured)
        self.type = 'King'
        self.direction_list = [self.move_n, self.move_s, self.move_w, self.move_e, self.move_nw, self.move_ne,
                               self.move_sw, self.move_se]
        self.max_move = 1


class Bishop(Piece):
    def __init__(self, player, space, captured=False):
        self.image = "images/white_bishop_static.png"
        super().__init__(self.image, player, space, captured)
        self.type = 'Bishop'
        self.direction_list = [self.move_nw, self.move_ne, self.move_sw, self.move_se]


class Rook(Piece):
    def __init__(self, player, space, captured=False):
        self.image = "images/white_rook_static.png"
        super().__init__(self.image, player, space, captured)
        self.type = 'Rook'
        self.direction_list = [self.move_n, self.move_s, self.move_w, self.move_e]


class Pawn(Piece):
    def __init__(self, player, space, captured=False):
        self.image = "images/white_pawn_static.png"
        self.en_passant_eligible = False
        super().__init__(self.image, player, space, captured)
        self.type = "Pawn"
        # Since Pawn's are the only one-direction piece, this adjusts for which side of the board you start on.
        self.direction_list = [self.move_forward]
        self.max_move = 1

    def move_forward(self, origin):
        if self.original_space.space_coord()[1] == 7:
            return origin[0], origin[1] - 1
        else:
            return origin[0], origin[1] + 1

    def move_forward_w(self, origin):
        forward = self.move_forward(origin)
        forward_w = self.move_w(forward)
        return forward_w

    def move_forward_e(self, origin):
        forward = self.move_forward(origin)
        forward_e = self.move_e(forward)
        return forward_e

    def ahead_space(self, spaces):
        origin = self.space.space_coord()
        ahead_coords = self.move_forward(origin)
        return spaces.get(ahead_coords)

    def neighboring_spaces(self, spaces):
        origin = self.space.space_coord()
        west_coords = self.move_w(origin)
        east_coords = self.move_e(origin)
        west_space = spaces.get(west_coords)
        east_space = spaces.get(east_coords)

        return west_space, east_space

    def diagonal_spaces(self, spaces):
        origin = self.space.space_coord()
        forward_e = self.move_forward_e(origin)
        forward_w = self.move_forward_w(origin)
        forward_e_space = spaces.get(forward_e)
        forward_w_space = spaces.get(forward_w)

        return forward_w_space, forward_e_space

    def move_path(self, origin, spaces, direction, max_move):
        move_list = []
        new_spot = spaces.get(direction(origin))

        while new_spot and len(move_list) < max_move:
            if new_spot.occupant:
                break
            move_list.append(new_spot)
            new_spot = spaces.get(direction(new_spot.space_coord()))
        return move_list

    def generate_move_list(self, spaces, max_move, en_passant_turn):
        # If pawn has not moved, it is eligible to move two positions:
        if self.space == self.original_space:
            super().generate_move_list(spaces, 2, en_passant_turn)

        # Traditional pawn moves:
        else:
            super().generate_move_list(spaces, max_move, en_passant_turn)

        # If a piece is diagonal, it can be captured:
        diagonals = self.diagonal_spaces(spaces)
        for diagonal in diagonals:
            if diagonal and diagonal.occupant and diagonal.occupant.player != self.player:
                self.move_list.append(diagonal)

        # If en_passant is eligible, add that to the list of moves:
        if en_passant_turn:
            west_space, east_space = self.neighboring_spaces(spaces)

            west_piece = (west_space.occupant if west_space else None)
            if west_piece and west_piece.type == 'Pawn' and west_piece.en_passant_eligible:
                fw_space = self.move_forward_w(self.space.space_coord())
                fw_space = spaces.get(fw_space)
                self.move_list.append(fw_space)

            east_piece = (east_space.occupant if east_space else None)
            if east_piece and east_piece.type == 'Pawn' and east_piece.en_passant_eligible:
                fe_space = self.move_forward_e(self.space.space_coord())
                fe_space = spaces.get(fe_space)
                self.move_list.append(fe_space)

    def move_piece(self, destination, game):
        # Pawns have the 'en_passant' rule to factor into the move: it is generally false but
        # could be 'True' for one turn.
        self.en_passant_eligible = False

        # Checks to see if Pawn will be eligible for 'en_passant' capture the next turn:
        if self.previous_position == self.original_space.position:
            spaces_moved = abs(destination.space_coord()[1] - self.space.space_coord()[1])
            if spaces_moved == 2:
                self.en_passant_eligible = True
                game.en_passant_turn = True

        # Checks to see if pawn performed an 'en_passant' with its move to account for the unusual capture.
        if destination in self.diagonal_spaces(game.spaces):
            neighbors = self.neighboring_spaces(game.spaces)
            for space in neighbors:
                piece = (space.occupant if space else None)
                if piece and piece.type == 'Pawn' and piece.en_passant_eligible:
                    piece.space.occupant = None
                    piece.got_captured(game)

        # Finally, Traditional move sequence for all pieces
        super().move_piece(destination, game)


class Knight(Piece):
    def __init__(self, player, space, captured=False):
        self.image = "images/white_knight_static.png"
        super().__init__(self.image, player, space, captured)
        self.type = "Knight"

    def generate_move_list(self, spaces, max_move, en_passant_turn):
        # self.move_list.append(self.space)
        origin = self.space.space_coord()
        move_options = [(origin[0]+2, origin[1]+1), (origin[0]+2, origin[1]-1), (origin[0]+1, origin[1]+2),
                        (origin[0]-1, origin[1]+2), (origin[0]-2, origin[1]+1), (origin[0]-2, origin[1]-1),
                        (origin[0]+1, origin[1]-2), (origin[0]-1, origin[1]-2)]

        for option in move_options:
            new_spot = spaces.get(option)
            if new_spot and new_spot.occupant and new_spot.occupant.player == self.player:
                continue
            if new_spot:
                self.move_list.append(new_spot)
