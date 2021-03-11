import unittest
from board import Game, Player, Rules, Board, CARDRULES, TERRAIN, SPECIALLOCATION, BOARDSECTIONS

board_env = """
. . W . . . . . . . . . W . . . . . . .
 . M W W . . . . . . . W . . C . . . . .
. M . . W . . . T . . W . . . . . . . .
 M M . W . . . . . . . W . . . . . . . .
. . M . W W . . . . W W . . . . . T . .
 . . . . . W W W W W . . C . . . . . . .
. T . . . . . . . . . . . . . . . M M M
 . . W . . C . . . . . . . . . M M M M M
. . W W . . . . M . . W . W . . . . M M
 . . . . . . . M M . . W W . . . . . M .
. . . . . . . . . . . . . . . . . . . .
 M . . . . . . . . . . . . T . . . . . .
M M . C . . . . . . . . . . . . . . . .
 M . . . . . . . . . M M . . . . . . . .
. . . W . . . . . . . . . . . . . W W W
 . . . . W . T . . . . . T . . . W . . .
. . . W . . . . . . . . . . . . W . C .
 C . . . . . . . . . . . . . . . W . . M
. . . . . M . . . . . . . . . . W . . .
 . . . . . M M . . . . . . . . . W W . .
"""

board_settlements = """
3 3 . . . . 4 . 4 . . 2 . . 4 . . 4 . 4
 3 . . . . 1 1 . . 4 2 . . 3 . 4 4 . . 4
3 . 2 2 . 1 1 1 . 3 2 . 4 3 . 1 4 . 4 .
 . . . . 2 2 . . . 2 2 . 3 . 1 1 1 . . .
. 4 . . . . 2 2 2 2 . . 3 . 1 4 . . . .
 . . . . . . . . . . . 3 . 1 . . 2 2 2 2
. . 1 1 1 1 . . 2 . . 4 . . . 2 2 . . .
 4 . . 4 . . 4 4 . . . . . . 2 . . . . .
. 4 . . . . . 4 . . . . . . . 2 2 2 . .
 . . . . . . . . . . . . . . . . . 2 . .
. . . 3 3 3 3 3 3 3 3 3 3 3 3 3 3 2 . 1
 . 3 3 . . . . . . . . 4 . . 2 . 2 4 1 .
. . . . . 4 . 4 . . . . . 1 2 4 2 1 1 .
 . . . 1 . 4 . . . . . . 1 2 . . 2 1 . .
. . . . 1 1 4 1 1 . . . 1 2 . . 2 . . .
 . . 1 1 . 1 . . 1 1 1 1 . . . 2 . . 4 .
. 1 1 . . 3 3 . . . . . . . . 2 . 4 . 3
 . 1 3 3 3 . 3 . 4 . 4 . 4 . . 2 . 1 1 .
4 3 3 4 . . 4 3 . . . . . . . 2 . . . .
 . . . 4 . . . 3 . . 4 4 . 4 . 2 . . . .
"""

def overlay_terrain(board):
    board_load = [row.split() for row in board_env.strip().split("\n")]
    for y in range(20):
        for x in range(20):
            if board_load[y][x] == '.':
                board_load[y][x] = board.board_env[y][x]

    board.board_env = board_load
    board.board_settlements = [row.split() for row in board_settlements.strip().split("\n")]

def set_default_terrain(board):
    board.board_env = [row.split() for row in board_env.strip().split("\n")]
    board.board_settlements = [row.split() for row in board_settlements.strip().split("\n")]

class TestRules(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestRules, self).__init__(*args, **kwargs)

        self.board = Board("quadrants")
        set_default_terrain(self.board)
        self.players = [ Player(ind) for ind in ["1", "2", "3", "4"] ]

    def test_possiblemove(self):
        set_default_terrain(self.board)
        move_options = self.board.getpossiblemove(self.players[0], SPECIALLOCATION.WATER)
        self.board.print_selection(move_options)
        self.assertEqual(len(move_options), 9)
        move_options = self.board.getpossiblemove(self.players[3], SPECIALLOCATION.MOUNTAIN)
        #self.board.print_selection(move_options)
        self.assertEqual(len(move_options), 8)

    def test_placing(self):
        set_default_terrain(self.board)
        self.assertEqual(self.board.place_settlement(self.players[0], 4, 4, SPECIALLOCATION.WATER), False)
        self.assertEqual(self.board.place_settlement(self.players[0], 2, 4, SPECIALLOCATION.WATER), True)
        #print(self.board)

    def test_resetplacing(self):
        set_default_terrain(self.board)
        self.assertEqual(self.board.reset_settlement(self.players[1], 8, 8), False)
        self.assertEqual(self.board.reset_settlement(self.players[2], 0, 0), True)

    def test_barnmove(self):
        overlay_terrain(self.board)
        self.assertEqual(len(self.board.getpossiblepaddockmove(self.players[3], 7, 12)), 0)
        moves = self.board.getpossiblepaddockmove(self.players[3], 12, 7)
        #self.board.print_selection(moves)

    def test_town_to_quadrant(self):
        self.assertEqual(self.board.town_to_boardsection(2, 8).name, self.board.quadrant_order[0])
        self.assertEqual(self.board.town_to_boardsection(4, 17).name, self.board.quadrant_order[1])
        self.assertEqual(self.board.town_to_boardsection(15, 6).name, self.board.quadrant_order[2])
        self.assertEqual(self.board.town_to_boardsection(15, 12).name, self.board.quadrant_order[3])

    def test_townquest(self):
        game = Game(4)
        #fix quadrants
        game.board.board_env = game.board.joinquadrants(["ORACLE", "PADDOCK", "HARBOR", "FARM"])
        print(game.board)

        self.assertEqual(game.place_settlement(2,7, TERRAIN.GRASS), True)
        self.assertEqual(game.player.settlements, 39)
        self.assertEqual(BOARDSECTIONS.ORACLE in game.player.towns, True)
        self.assertEqual(game.place_settlement(2,8, TERRAIN.GRASS), True)
        self.assertEqual(len(game.player.towns), 1)
        self.assertEqual(game.place_settlement(0,6, TERRAIN.GRASS), False)
        self.assertEqual(game.place_settlement(1,6, TERRAIN.GRASS), True)
        self.assertEqual(game.board.resulting_board()[3][7], 't')
        print(game.board)
        
    def test_rulecards(self):
        set_default_terrain(self.board)
        #print(self.board)

        

        rule_list = [
                        [1, 3, 7],
                        [1, 3, 8],
                        #[1, 4, 7],
                        #[1, 4, 8],
                        [1, 5, 7],
                        [1, 5, 8],
                        [1, 6, 7],
                        [1, 6, 8],
                        [2, 3, 7],
                        [2, 3, 8],
                        #[2, 4, 7],
                        #[2, 4, 8],
                        [2, 5, 7],
                        [2, 5, 8],
                        [2, 6, 7],
                        [2, 6, 8],
                    ]

        score = [
                    [52, 46, 43, 62],
                    [49, 51, 45, 35],
                    #[43, 37, 41, 61],
                    #[40, 42, 43, 34],
                    [57, 61, 45, 75],
                    [54, 66, 47, 48],
                    [57, 25, 48, 84],
                    [54, 30, 50, 57],
                    [52, 34, 59, 56],
                    [49, 39, 61, 29],
                    #[43, 25, 57, 55],
                    #[40, 30, 59, 28],
                    [57, 49, 61, 69],
                    [54, 54, 63, 42],
                    [57, 13, 64, 78],
                    [54, 18, 66, 51],
                ]

        for i, rule in enumerate(rule_list):
            enum_rule = [CARDRULES(x) for x in rule]
            rules = Rules(self.board, enum_rule)
            score_out = rules.score(self.players)
            #print(rules.player_score_per_rule)
            #print(score_out)
            self.assertEqual(score[i], score_out)

if __name__ == '__main__':
    unittest.main()

