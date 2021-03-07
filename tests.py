import unittest
from board import Player, Rules, Board, CARDRULES

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

class TestRules(unittest.TestCase):

    def test_upper(self):

        board = Board("quadrants")
        board.board_env = [row.split() for row in board_env.strip().split("\n")]
        board.board_settlements = [row.split() for row in board_settlements.strip().split("\n")]
        print(board)
        players = [ Player(ind) for ind in ["1", "2", "3", "4"] ]

        

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
            rules = Rules(board, enum_rule)
            score_out = rules.score(players)
            print(rules.player_score_per_rule)
            print(score_out)
            self.assertEqual(score[i], score_out)

if __name__ == '__main__':
    unittest.main()

