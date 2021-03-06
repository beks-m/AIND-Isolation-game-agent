"""This file contains all the classes you must complete for this project.

You can use the test cases in agent_test.py to help during development, and
augment the test suite with your own test cases to further test your code.

You must test your agent's strength against a set of agents with known
relative strength using tournament.py and include the results in your report.
"""
import random


class Timeout(Exception):
    """Subclass base exception for code clarity."""
    pass

def attacking_score(game, player):
    """Calculate the heuristic value of a game state from the point of view
    of the given player.

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    ----------
    float
        The heuristic value of the current game state to the specified player.
    """

    if game.is_loser(player):
        return float("-inf")

    if game.is_winner(player):
        return float("inf")

    # minimize opponent’s open moves
    return(float(-len(game.get_legal_moves(game.get_opponent(player)))))

def deeper_score(game, player):
    """Calculate the heuristic value of a game state from the point of view
    of the given player.

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    ----------
    float
        The heuristic value of the current game state to the specified player.
    """

    if game.is_loser(player):
        return float("-inf")

    if game.is_winner(player):
        return float("inf")

    # evaluate not on just number of open moves, but how good these open moves are
    # by summing the scores of player’s currently available moves
    score = 0
    for move in game.get_legal_moves(player):
        score += len(game.forecast_move(move).get_legal_moves(player))
        score -= len(game.forecast_move(move).get_legal_moves(game.forecast_move(move).get_opponent(player)))

    return float(score)

def custom_score(game, player):
    """Calculate the heuristic value of a game state from the point of view
    of the given player.

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    ----------
    float
        The heuristic value of the current game state to the specified player.
    """

    if game.is_loser(player):
        return float("-inf")

    if game.is_winner(player):
        return float("inf")

    # standard improved score
    score = len(game.get_legal_moves(player)) - len(game.get_legal_moves(game.get_opponent(player)))

    # Lean towards center of the board
    # Choice farthest to the center will get minimal score
    center_x = game.width/2
    center_y = game.height/2
    row, col = game.get_player_location(player)
    score -= abs(row-center_x) * 0.1
    score -= abs(col-center_y) * 0.1

    return float(score)


class CustomPlayer:
    """Game-playing agent that chooses a move using your evaluation function
    and a depth-limited minimax algorithm with alpha-beta pruning. You must
    finish and test this player to make sure it properly uses minimax and
    alpha-beta to return a good move before the search time limit expires.

    Parameters
    ----------
    search_depth : int (optional)
        A strictly positive integer (i.e., 1, 2, 3,...) for the number of
        layers in the game tree to explore for fixed-depth search. (i.e., a
        depth of one (1) would only explore the immediate sucessors of the
        current state.)

    score_fn : callable (optional)
        A function to use for heuristic evaluation of game states.

    iterative : boolean (optional)
        Flag indicating whether to perform fixed-depth search (False) or
        iterative deepening search (True).

    method : {'minimax', 'alphabeta'} (optional)
        The name of the search method to use in get_move().

    timeout : float (optional)
        Time remaining (in milliseconds) when search is aborted. Should be a
        positive value large enough to allow the function to return before the
        timer expires.
    """

    def __init__(self, search_depth=3, score_fn=custom_score,
                 iterative=True, method='minimax', timeout=10.):
        self.search_depth = search_depth
        self.iterative = iterative
        self.score = score_fn
        self.method = method
        self.time_left = None
        self.TIMER_THRESHOLD = timeout

    def get_move(self, game, legal_moves, time_left):
        """Search for the best move from the available legal moves and return a
        result before the time limit expires.

        This function must perform iterative deepening if self.iterative=True,
        and it must use the search method (minimax or alphabeta) corresponding
        to the self.method value.

        **********************************************************************
        NOTE: If time_left < 0 when this function returns, the agent will
              forfeit the game due to timeout. You must return _before_ the
              timer reaches 0.
        **********************************************************************

        Parameters
        ----------
        game : `isolation.Board`
            An instance of `isolation.Board` encoding the current state of the
            game (e.g., player locations and blocked cells).

        legal_moves : list<(int, int)>
            A list containing legal moves. Moves are encoded as tuples of pairs
            of ints defining the next (row, col) for the agent to occupy.

        time_left : callable
            A function that returns the number of milliseconds left in the
            current turn. Returning with any less than 0 ms remaining forfeits
            the game.

        Returns
        ----------
        (int, int)
            Board coordinates corresponding to a legal move; may return
            (-1, -1) if there are no available legal moves.
        """

        self.time_left = time_left

        # Perform any required initializations, including selecting an initial
        # move from the game board (i.e., an opening book), or returning
        # immediately if there are no legal moves

        # Check if there are available moves left, if not -> forfeit
        if len(legal_moves) == 0:
            return (-1, -1)

        # Assign initial best move, so that we have something to return if we are out of time
        best_move = random.choice(game.get_legal_moves())

        try:
            # The search method call (alpha beta or minimax) should happen in
            # here in order to avoid timeout. The try/except block will
            # automatically catch the exception raised by the search method
            # when the timer gets close to expiring

            # If we need to do iterative deepening search
            if self.iterative:
                # Start with minimal depth and gradually increase it to get better move
                depth = 0
                while True:
                    if self.method == 'minimax':
                        score, best_move = self.minimax(game, depth, True)
                    if self.method == 'alphabeta':
                        score, best_move = self.alphabeta(game, depth, float("-inf"), float("inf"), True)
                    depth += 1
            else:
                if self.method == 'minimax':
                    score, best_move = self.minimax(game, self.search_depth, True)

                if self.method == 'alphabeta':
                    score, best_move = self.alphabeta(game, self.search_depth, float("-inf"), float("inf"), True)

        except Timeout:
            # Handle any actions required at timeout, if necessary
            return best_move

        return best_move


    def minimax(self, game, depth, maximizing_player=True):
        """Implement the minimax search algorithm as described in the lectures.

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        maximizing_player : bool
            Flag indicating whether the current search depth corresponds to a
            maximizing layer (True) or a minimizing layer (False)

        Returns
        ----------
        float
            The score for the current search branch

        tuple(int, int)
            The best move for the current branch; (-1, -1) for no legal moves
        """

        # check the timer on every iteration, raise Timeout exception if time is running out
        if self.time_left() < self.TIMER_THRESHOLD:
            raise Timeout()

        # if we reached the search depth limit or the game tree bottom, then return the heuristic value for forecast state and move
        if depth == 0 or game.utility(self) != 0:
            return self.score(game, self), game.__last_player_move__[game.inactive_player]

        # Instantiate best_move, so that we can safely return something in the end of function
        best_move = game.get_legal_moves()[0]

        # Recursive function that compares the heuristic values and chooses best move accordingly
        # Check if we are on max node or min node, then act act accordingly
        # ~ Max-Value function described in aima-pseudocode repository
        if maximizing_player:
            # Choose minimal initial best_score, so we have something to compare to when iterating
            best_score = float("-inf")
            for move in game.get_legal_moves():
                # Start the recursive iteration of game tree
                score, new_move = self.minimax(game.forecast_move(move), depth-1, not maximizing_player)
                # Assign to best option the node (move) with the maximum score
                if score > best_score:
                    best_score = score
                    best_move = move
        # Almost the same logic if we are on min node
        # ~ Min-Value function described in aima-pseudocode repository
        else:
            # Choose maximal initial best_score, so we have something to compare to when iterating
            best_score = float("inf")
            for move in game.get_legal_moves():
                # Start the recursive iteration of game tree
                score, new_move = self.minimax(game.forecast_move(move), depth-1, not maximizing_player)
                # Assign to best option the node (move) with the minimum score
                if score < best_score:
                    best_score = score
                    best_move = move

        return best_score, best_move


    def alphabeta(self, game, depth, alpha=float("-inf"), beta=float("inf"), maximizing_player=True):
        """Implement minimax search with alpha-beta pruning as described in the
        lectures.

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        alpha : float
            Alpha limits the lower bound of search on minimizing layers

        beta : float
            Beta limits the upper bound of search on maximizing layers

        maximizing_player : bool
            Flag indicating whether the current search depth corresponds to a
            maximizing layer (True) or a minimizing layer (False)

        Returns
        ----------
        float
            The score for the current search branch

        tuple(int, int)
            The best move for the current branch; (-1, -1) for no legal moves
        """

        # check the timer on every iteration, raise Timeout exception if time is running out
        if self.time_left() < self.TIMER_THRESHOLD:
            raise Timeout()

        # if we reached the search depth limit or the game tree bottom, then return the heuristic value for forecast state and move
        if depth == 0 or game.utility(self) != 0:
            return self.score(game, self), game.__last_player_move__[game.inactive_player]


        # Instantiate best_move, so that we can safely return something in the end of function
        best_move = game.get_legal_moves()[0]

        # Recursive function that compares the heuristic values and chooses best move accordingly
        # Minimax algorithm as above with Alpha-beta pruning
        # Check if we are on max node or min node, then act act accordingly
        if maximizing_player:
            # Choose minimal initial best_score, so we have something to compare to when iterating
            best_score = float("-inf")
            for move in game.get_legal_moves():
                # Start the recursive iteration of game tree
                score, new_move = self.alphabeta(game.forecast_move(move), depth-1, alpha, beta, not maximizing_player)
                if score > best_score:
                    best_score = score
                    best_move = move
                if best_score >= beta:
                    return best_score, best_move
                alpha = max([alpha, best_score])
        # Almost the same logic if we are on min node
        else:
            # Choose maximal initial best_score, so we have something to compare to when iterating
            best_score = float("inf")
            for move in game.get_legal_moves():
                # Start the recursive iteration of game tree
                score, new_move = self.alphabeta(game.forecast_move(move), depth-1, alpha, beta, not maximizing_player)
                if score < best_score:
                    best_score = score
                    best_move = move
                if best_score <= alpha:
                    return best_score, best_move
                beta = min([beta, best_score])

        return best_score, best_move
