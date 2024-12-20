'''
Player 1 = Non AI player
Player 2 = AI player
'''


class Game:
    def __init__(self, N):
        '''
        Initializing the game.
        int N: the number of dots in the game
        '''

        # creating a set of all the possible lines to draw
        self.available = set()
        for i in range(N):
            for j in range(i+1, N):
                self.available.add((i, j))

        # creating a state variable game for keeping track of who drew what
        # game[3][4] = 2 means that player 2 drew a line between 3,4
        self.game = {i: {} for i in range(N)}

        # variables to keep the history of the game
        # helpful for backtracking and undoing moves
        self.last_player = []
        self.last_x = []
        self.last_y = []

    # checking if the player who made the last move lost the game
    def lost(self):
        '''
        Checks if the player who drew the last line, lost the game
        Returns:
        False: The game is still ongoing
        int N: The player who lost (1,2)
        True: as a representation for ties (not possible in case of 6 dots)
        '''
        # if no moves has been played, the game is still ongoing
        if not self.last_x:
            return False

        # x,y are the ends of the last drawn line
        x, y = self.last_x[-1], self.last_y[-1]

        # checking to see if there are two lines from the same player
        # which create a triangle with this new drawn line
        for j in self.game[x]:
            if (self.game[j].get(y, -1)
                == self.game[j].get(x, -1)
                == self.last_player[-1]):

                # if there are, then the player lost
                return self.last_player[-1]

        # if there was no triangle but no other available moves = tie
        if len(self.available) == 0:
            return True

        # otherwise, the game is ongoing
        return False

    # Drawing a line
    def draw_line(self, x, y, player):
        '''
        Takes:
            int x: the beginning of the line
            int y: end of the line
            int player:  the one who drew the line
        Returns:
            False: the line could not be drawn
            True: the line was drawn
        '''
        # checking if there is already and existing line
        # or if the requested dots are out of bound
        if x >= len(self.game) or y >= len(self.game) or x in self.game[y]:
            return False

        # adding the drawn line to history and removing from available moves
        self.game[x][y] = player
        self.game[y][x] = player
        self.last_player.append(player)
        self.last_x.append(x)
        self.last_y.append(y)
        self.available.remove((min(x, y), max(x, y)))
        return True

    def undo_move(self):
        '''
        Undoing the last move
        '''

        # removing the history that was just created
        x = self.last_x.pop()
        y = self.last_y.pop()
        self.last_player.pop()
        del self.game[x][y]
        del self.game[y][x]

        # returning the removed line as available
        self.available.add((min(x, y), max(x, y)))
        return True

    # get available lines to draw
    def get_allowed_lines(self):
        '''
        returns the set of available lines to draw
        '''
        return self.available


def determine_best_next(game: Game,
                        max_min: str = "MAX",
                        alpha: float = -float("inf"),
                        beta: float = float("inf"),
                        depth: int = 0,
                        difficulty: int = 1):
    '''
    The AI solver: Min-Max with alpha-beta pruning and limited depth
    Takes:
        Game game: Game instance
        str max_min: determining if this is a maximization setp or not
        float alpha: alpha parameter
        float beta: beta parameter
        int depth: the current depth (start at 0)
        int difficulty: the max depth
    Returns:
        None or tuple: best next move
        float or int: the best (max or min) outcome of the state
    '''
    # the state of the game if someone lost
    end = game.lost()

    # if the game ended, we return the utility
    if end:
        # if it is not an integer, it means a tie, so 0.5 is the utility
        if not isinstance(end, int):
            return None, 0.5

        # if player 2 lost (AI agent), then we return 0 utility
        elif end == 2:
            return None, 0

        # if player 2 won (AI agent), we return utility 1
        else:
            return None, 1

    # get a copy of available moves
    copy = game.available.copy()

    # applying the heuristic if the max depth is reached
    if depth >= difficulty:
        wins_1 = 0
        wins_2 = 0
        for x, y in copy:

            # potential losses of player 1
            game.draw_line(x, y, 1)
            if game.lost():
                wins_2 += 1
            game.undo_move()

            # potential losses for player 2, the AI
            game.draw_line(x, y, 2)
            if game.lost():
                wins_1 += 1
            game.undo_move()

        total = wins_1+wins_2
        # returning the fraction of winning for AI that we are maximizing
        return None, wins_2/(total) if total > 0 else 0.5

    to_play = None

    # taking turns, with the human always starting
    if len(game.last_player) == 0 or game.last_player[-1] == 2:
        player = 1
    else:
        player = 2

    # maximizing case
    if max_min == "MAX":
        res = -1

        # trying all available moves recursively
        for x, y in copy:
            game.draw_line(x, y, player)
            value = determine_best_next(game, "MIN", alpha, beta, depth+1, difficulty=difficulty)[1]
            game.undo_move()

            if value >= res:
                res = value
                to_play = (x, y)
            alpha = max(alpha, value)

            # pruning in alpha-beta pruning
            if alpha > beta:
                break
        return to_play, res

    # minimizing case
    else:
        res = 2

        # trying all available moves recursively
        for x, y in copy:
            game.draw_line(x, y, player)
            value = determine_best_next(game, "MAX", alpha, beta, depth+1, difficulty=difficulty)[1]
            game.undo_move()

            if value <= res:
                res = value
                to_play = (x, y)
            beta = min(beta, value)

            # pruning in alpha-beta pruning
            if beta < alpha:
                break

        return to_play, res
