# Author: Kaewan Gardi
# Date: 11/30/2020
# Description:  Contains a class named FocusGame for playing a board game called Focus/Dominion.
#               Contains a class named Player defining players used in FocusGame
#

class FocusGame:
    """
    Represents an instance of the game Focus/Domination.
    Uses the Player class to more easily access/modify information on the players and their states.
    """

    def __init__(self, player1, player2):
        """
        Parameter1: player 1 info provided as tuple formatted as (name, color)
        Parameter2: Player 2 info provided as tuple formatted as (name, color)
        Initializes a game of Focus with a new gameboard.
        Creates two player objects and stores in dictionary with name as key, object as value.
        """
        # Get colors to ease readability in self._board initialization
        c1 = player1[1]
        c2 = player2[1]
        self._board = [[[c1], [c1], [c2], [c2], [c1], [c1]],
                       [[c2], [c2], [c1], [c1], [c2], [c2]],
                       [[c1], [c1], [c2], [c2], [c1], [c1]],
                       [[c2], [c2], [c1], [c1], [c2], [c2]],
                       [[c1], [c1], [c2], [c2], [c1], [c1]],
                       [[c2], [c2], [c1], [c1], [c2], [c2]]]
        self._players = {player1[0]: Player(player1[0], player1[1]),
                         player2[0]: Player(player2[0], player2[1])}
        self._turn = player1[0]

    def display_board(self):
        """
        Displays the game board for the purposes of debugging.
        Will likely be removed on assignment completion
        """
        for row in self._board:
            print(row)

    def move_piece(self, player_name, start_pos, finish_pos, piece_count):
        """
        Performs the requested move if it is valid and checks if winning move
        Parameter1: name of player making the move
        Parameter2: tuple representing coordinate position move is being made from
        Parameter3: tuple representing coordinate position of destination
        Parameter4: number of pieces to be moves
        Returns: Returns False if move is invalid
                 Returns "successfully moved" if move is good,
                 Returns win message if player won
        """
        # Validate move
        if self.is_valid(player_name, start_pos, finish_pos, piece_count) is False:
            return False

        # Fetch start location's stack to help readability
        spot = self._board[start_pos[0]][start_pos[1]]

        # Remove/grab pieces to move
        move_stack = []
        for piece_index in range(-piece_count, 0):
            move_stack.append(spot.pop(piece_index))

        # Call make_single_move or make_multi_move
        if len(move_stack) > 1:
            self.make_multi_move(self._players[player_name], move_stack, finish_pos)
        else:
            self.make_single_move(self._players[player_name], finish_pos)

        # Check for winner
        if self._players[player_name].get_captured() >= 5:
            return str(player_name) + " wins!"

        # Switch player and end turn
        self.switch_player()
        return "successfully moved"

    def is_valid(self, player_name, start_pos, finish_pos, piece_count):
        """
        Validates the requested move.
        Parameter1: name of player making move
        Parameter2: tuple representing coordinate position move is being made from
        Parameter3: tuple representing coordinate position of destination
        Parameter4: number of pieces to be moves
        Returns: Returns False if move is invalid
        """
        # Check if correct player's turn
        if self._turn != player_name:
            return False

        # Check if locations are real board locations
        start_good = 0 <= start_pos[0] <= 5 and 0 <= start_pos[1] <= 5
        finish_good = 0 <= finish_pos[0] <= 5 and 0 <= finish_pos[1] <= 5

        if start_good is False or finish_good is False:
            return False

        # Check if player owns stack
        if self._board[start_pos[0]][start_pos[1]][-1] != self._players[player_name].get_color():
            return False

        # Check invalid number of pieces
        if len(self._board[start_pos[0]][start_pos[1]]) < piece_count:
            return False

        # Check invalid move distance
        if abs(start_pos[0] - finish_pos[0]) != piece_count and abs(start_pos[1] - finish_pos[1]) != piece_count:
            return False

    def show_pieces(self, position):
        """
        Parameter1: tuple representing coordinates of the position
        Returns a list of pieces at the given board position as [bottom ... top]
        Returns false if location is invalid
        """
        row, column = position
        if row < 0 or row > 5 or column < 0 or column > 5:
            return False
        return self._board[row][column]

    def show_reserve(self, player_name):
        """
        Parameter1: player name string
        Returns the number of reserve pieces the player has
        """
        if player_name in self._players.keys():
            return self._players[player_name].get_reserves()
        else:
            return False

    def show_captured(self, player_name):
        """
        Parameter1: player name string
        Returns the number of captured pieces the player has
        """
        if player_name in self._players.keys():
            return self._players[player_name].get_captured()
        else:
            return False

    def reserved_move(self, player_name, location):
        """
        If possible, removes a piece from the player's reserve and place it at the given location
        Parameter1: name of player making the move
        Parameter2: tuple representing coordinate position to place reserve at
        Returns "No pieces in reserve" if move cannot be made
        """
        # Check correct player's turn
        if player_name != self._turn:
            return False

        # Check if location is valid
        if location[0] < 0 or location[0] > 5 or location[1] < 0 or location[1] > 5:
            return False

        # Check if player has any reserves
        if self._players[player_name].get_reserves() == 0:
            return False

        # Make move
        self._players[player_name].remove_reserve()
        self.make_single_move(self._players[player_name], location)

        # Switch player and end turn
        self.switch_player()
        return "successfully moved"

    def make_single_move(self, player, location):
        """
        Makes a move of one piece. Clears bottom rows as needed
        Parameter1: player object of player making the move
        Parameter2: tuple representing coordinate position to place piece at
        """""
        # Fetch location's stack to help readability
        spot = self._board[location[0]][location[1]]

        # Add piece to the location
        spot.append(player.get_color())

        # Capture/Reserve bottom piece if stack is too large
        if len(spot) > 5:
            if spot[0] == player.get_color():
                self.reserve_bottom(player, location)
            else:
                self.capture_bottom(player, location)

    def make_multi_move(self, player, stack, location):
        """
        Moves the stack of pieces to the specified location. Clears bottom rows as needed
        Parameter1: player object of player making the move
        Parameter2: list of pieces being moved
        Parameter3: tuple representing coordinate position to place pieces
        """
        # Add new pieces to the top of the current stack
        self._board[location[0]][location[1]] += stack

        # Capture/Reserve bottom pieces if stack is too large
        while len(self._board[location[0]][location[1]]) > 5:
            if self._board[location[0]][location[1]][0] == player.get_color():
                self.reserve_bottom(player, location)
            else:
                self.capture_bottom(player, location)

    def reserve_bottom(self, player, location):
        """
        Remove bottom piece and add it to players reserve count
        Parameter1: player object of player making the move
        Parameter2: tuple representing coordinate position
        """
        self._board[location[0]][location[1]] = self._board[location[0]][location[1]][1:]
        player.add_reserve()

    def capture_bottom(self, player, location):
        """
        Remove bottom piece and add it to players capture count
        Parameter1: player object of player making the move
        Parameter2: tuple representing coordinate position"""
        self._board[location[0]][location[1]] = self._board[location[0]][location[1]][1:]
        player.add_captured()

    def switch_player(self):
        """Switches self._turn to the next player"""
        player_names = list(self._players.keys())

        if self._turn == player_names[0]:
            self._turn = player_names[1]
        else:
            self._turn = player_names[0]


class Player:
    """
    Represents a player for the FocusGame class.
    Contains methods to initialize a player and view/modify their properties.
    """
    def __init__(self, name, color):
        """
        Parameter1: player name as a string
        Parameter2: player color as a string
        Initializes a new Focus game player
        """
        self._name = name
        self._color = color
        self._captured = 0
        self._reserves = 0

    def get_name(self):
        """Returns player's name"""
        return self._name

    def get_reserves(self):
        """Returns player's number of reserve pieces"""
        return self._reserves

    def add_reserve(self):
        """Add 1 to player's reserve count"""
        self._reserves += 1

    def remove_reserve(self):
        """Removes 1 from player's reserve count"""
        self._reserves -= 1

    def get_captured(self):
        """Returns player's number of captured pieces"""
        return self._captured

    def add_captured(self):
        """Add 1 to player's reserve count"""
        self._captured += 1

    def get_color(self):
        """Returns the player's color"""
        return self._color
