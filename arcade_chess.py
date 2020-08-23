"""
Simple Chess Game
"""
import arcade
import PIL

from arcade import Texture
from pieces import Queen, King, Rook, Bishop, Knight, Pawn
import constants


class ArcadeChess(arcade.Window):
    """ Main application class. """

    def __init__(self):
        super().__init__(constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT, constants.SCREEN_TITLE)

        self.spaces = dict()

        self.space_list: arcade.SpriteList = arcade.SpriteList()
        self.piece_list = arcade.SpriteList()
        self.player_list = []
        self.move_list = []

        self.en_passant_turn = False
        self.piece_held = None
        self.active_player = None

        arcade.set_background_color(arcade.color.AMAZON)

    def setup(self, p1_name, p1_color, p2_name, p2_color):
        """ Set up the game here. Call this function to restart the game. """
        # Setup Players:
        p1 = Player(p1_name, p1_color)
        p2 = Player(p2_name, p2_color)
        self.player_list.extend((p1, p2))
        self.active_player = self.player_list[0]

        # Setup playing board and the 'space' sprites
        for r in range(1, constants.BOARD_ROWS + 1):
            for c in range(1, constants.BOARD_COLUMNS + 1):
                if (r + c) % 2 == 0:
                    color = arcade.color.TAN
                else:
                    color = arcade.color.AVOCADO
                space = Space(c, r, color)
                #Formula here sets the centerpoint of each space
                space.set_position((2*c-1)/(constants.BOARD_COLUMNS*2)*constants.BOARD_HEIGHT,
                                   (2*r-1)/(constants.BOARD_ROWS*2)*constants.BOARD_WIDTH)
                self.space_list.append(space)
                self.spaces[(c,r)] = space

        # Setup starting pieces
        # This is clunky.  But it works.
        starting_pieces_1 = [(Queen, (5, 1)), (King, (4,1)), (Bishop, (3,1)), (Bishop, (6,1)), (Rook, (1,1)),
                             (Rook, (8,1)), (Knight, (2,1)), (Knight, (7,1))]
        for i in range(1, 9):
            starting_pieces_1.append((Pawn, (i,2)))

        starting_pieces_2 = [(Queen, (5, 8)), (King, (4,8)), (Bishop, (3,8)), (Bishop, (6,8)), (Rook, (1,8)),
                             (Rook, (8,8)), (Knight, (2,8)), (Knight, (7,8))]
        for i in range(1, 9):
            starting_pieces_2.append((Pawn, (i,7)))

        for sp in starting_pieces_1:
            piece = sp[0](self.player_list[0], self.spaces[sp[1]])
            piece.set_position(piece.space.center_x, piece.space.center_y)
            piece._set_color(p1.color)
            self.spaces[sp[1]].occupant = piece
            self.piece_list.append(piece)

        for sp in starting_pieces_2:
            piece = sp[0](self.player_list[1], self.spaces[sp[1]])
            piece.set_position(piece.space.center_x, piece.space.center_y)
            piece._set_color(p2.color)
            self.spaces[sp[1]].occupant = piece
            self.piece_list.append(piece)

    def on_draw(self):
        """ Render the screen. """
        arcade.start_render()
        self.space_list.draw()
        self.piece_list.draw()

    def on_mouse_press(self, x, y, button, key_modifiers):
        """ User moves mouse """
        # If you are not holding a piece and click it tries to pick up a piece:
        if not self.piece_held:
            pieces_near_click = arcade.get_sprites_at_point((x,y), self.piece_list)
            piece = (pieces_near_click[0] if pieces_near_click else None)

            if piece and piece.player == self.active_player:
                self.piece_held = piece
                self.set_mouse_visible(False)  # Piece is now the 'cursor' and the mouse is distracting
                self.piece_held.pickup(self.spaces, self.en_passant_turn)


        # If you are already holding a piece when you click:
        else:
            # Snapping held chess piece to the closest board position
            destination, position = arcade.get_closest_sprite(self.piece_held, self.space_list)
            self.set_mouse_visible(True)

            # If the attempted movement is not legal, this returns it to the originating location)
            if self.get_space(destination.space_coord()) not in self.piece_held.move_list:
                self.piece_held.return_to_previous_position()

            elif destination.occupant and destination.occupant.player == self.active_player:
                self.piece_held.return_to_previous_position()

            else:
                # No longer an en_passant_turn (if it ever was)
                self.en_passant_turn = False
                # The capture function manages all legal placements; it can be considered the end of a turn.
                capture(self, self.piece_held, destination)

            # 'Lets Go' of the piece to complete the click and reset the board.
            for space in self.piece_held.move_list:
                space.return_original_color()
            self.piece_held.move_list = []
            self.piece_held.previous_position = None
            self.piece_held = None

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        """ User moves mouse """
        # If we are holding a piece, move it with the mouse
        if self.piece_held:
            self.piece_held.center_x += dx
            self.piece_held.center_y += dy

    def get_space_list(self):
        return self.space_list

    def get_space(self, space_coord):
        return self.spaces.get(space_coord)

    def next_player(self):
        if self.active_player == self.player_list[0]:
            return self.player_list[1]
        else:
            return self.player_list[0]

    def active_pieces(self):
        active_pieces = []
        for piece in self.piece_list:
            if piece.player == self.active_player:
                active_pieces.append(piece)
        return active_pieces

    def opponent_king(self):
        for piece in self.piece_list:
            if piece.type == 'King' and piece.player != self.active_player:
                return piece


class Space(arcade.SpriteSolidColor):
    """ Chess-space sprite """

    def __init__(self, row_number, column_number, color, occupant=None):
        """ Space constructor """
        super().__init__(constants.SPACE_WIDTH, constants.SPACE_HEIGHT, color)
        self.row_number = row_number
        self.column_number = column_number
        self.occupant = occupant
        self.permanent_color = color
        self.temp_color = None

    def space_coord(self):
        return self.row_number, self.column_number

    def set_temp_color(self, color):
        image = PIL.Image.new('RGBA', (constants.SPACE_WIDTH, constants.SPACE_HEIGHT), color)
        self.texture = Texture(f"Solid-{color[0]}-{color[1]}-{color[2]}", image)

    def return_original_color(self):
        image = PIL.Image.new('RGBA', (constants.SPACE_WIDTH, constants.SPACE_HEIGHT), self.permanent_color)
        self.texture = Texture(f"Solid-{self.permanent_color[0]}-{self.permanent_color[1]}-{self.permanent_color[2]}"
                               , image)

    def get_space_player(self):
        if self.occupant:
            return self.occupant.player
        else:
            return None


class Player:
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.pieces_lost = []


def capture(game, piece, space):
    'Called whenever a legal move is made: it effectively determines when a turn is complete and a new turn begins'

    # Remove the color-code from the piece's origin space:
    piece.space.return_original_color()

    # If the space captured is unoccupied:
    if space.get_space_player() is None:
        piece.move_piece(space, game)

    # If the space captured is owned by the opponent
    else:
        captured_piece = space.occupant
        captured_piece.got_captured(game)
        piece.move_piece(space, game)

    # Sets the new player, a new turn begins here effectively.
    game.active_player = game.next_player()


def main():
    """ Main method """
    window = ArcadeChess()
    window.setup('Justin', arcade.color.WHITE, 'Cassandra', arcade.color.SMOKY_BLACK)
    arcade.run()


if __name__ == "__main__":
    main()