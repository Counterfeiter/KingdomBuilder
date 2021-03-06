import unittest
import random
from copy import deepcopy
from kingdombuilder import Board
from kingdombuilder import Player
from kingdombuilder import Rules
from kingdombuilder import Game, DOACTION

from kingdombuilder import CARDRULES, TERRAIN, SPECIALLOCATION, BOARDSECTIONS

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

board_mixed = """
G G F F F W G F F B S S S D D W D D D D
 G B F F W G F F B B M M S D D W D D D D
G B B F W G G B B B M M S M M W D D T B
 B B F F W G M B D D M S M M W M D B B B
S B C F W G D D D D S S F F W M M S B B
 S S F W G G M M D D S 1 1 W S S S M B B
S S W W W G D D D S S t F 1 W B B B B B
 W W 1 1 W W T S M S G G F W G C G B G F
W D C G W M W S S S G G F F W G G G G F
 W D D W W W W S S S G G F F W G G G F F
G G G F F W G F F F D D S W W F F F G G
 G G G C F W G F F F D C S W F F F T G G
G B B G F F W G G F S S S B B B F S B B
 B B S G F W B T F F S S B B W D D S S B
B B B S S W B B W W S 2 2 W B B D D S S
 M M S G G W W W D D G 2 t B W B W D D S
S S S M G B B B D D G G 2 F B B W W D D
 S S C D M D B B S S G G F F M W W W D W
W W W D D D D M S S G M F F W W W W W W
 W W W W D D D D D S F F F W W W W W W W
"""

def overlay_terrain(board : Board):
    board_load = [row.split() for row in board_env.strip().split("\n")]
    for y in range(20):
        for x in range(20):
            if board_load[y][x] == '.':
                board_load[y][x] = board.board_env[y][x]

    board.board_env = board_load
    board.board_settlements = [row.split() for row in board_settlements.strip().split("\n")]

def set_mixed(board : Board):
    board_load = [row.split() for row in board_mixed.strip().split("\n")]
    player_list = ["1", "2", "3","4"]
    for y in range(20):
        for x in range(20):
            if board_load[y][x] in player_list:
                board.board_settlements[y][x] = board_load[y][x]
            else:
                board.board_settlements[y][x] = ' '
                board.board_env[y][x] = board_load[y][x]

def set_default_terrain(board : Board):
    board.board_env = [row.split() for row in board_env.strip().split("\n")]
    board.board_settlements = [row.split() for row in board_settlements.strip().split("\n")]

class TestRules(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestRules, self).__init__(*args, **kwargs)

        self.board = Board()
        self.num_games_selfplay = 30
        set_default_terrain(self.board)
        self.players = [ Player(ind) for ind in ["1", "2", "3", "4"] ]

    def test_possiblemove(self):
        set_default_terrain(self.board)
        move_options = self.board.getpossiblemove(self.players[0], SPECIALLOCATION.WATER)
        #self.board.print_selection(move_options)
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

    def test_town_to_quadrant(self):
        self.assertEqual(self.board.town_to_boardsection(2, 8).name, self.board.quadrant_order[0])
        self.assertEqual(self.board.town_to_boardsection(4, 17).name, self.board.quadrant_order[1])
        self.assertEqual(self.board.town_to_boardsection(15, 6).name, self.board.quadrant_order[2])
        self.assertEqual(self.board.town_to_boardsection(15, 12).name, self.board.quadrant_order[3])

    def test_townquest(self):
        game = Game(4)
        #fix quadrants
        game.board.board_env = game.board.joinquadrants(["ORACLE", "PADDOCK", "HARBOR", "FARM"], [False] * 4)
        #print(game.board)

        self.assertEqual(game.place_settlement(2,7, TERRAIN.GRASS), True)
        self.assertEqual(game.player.settlements, 39)
        self.assertEqual(BOARDSECTIONS.ORACLE in game.player.towns, True)
        self.assertEqual(game.place_settlement(2,8, TERRAIN.GRASS), True)
        self.assertEqual(len(game.player.towns), 1)
        self.assertEqual(game.place_settlement(0,6, TERRAIN.GRASS), False)
        self.assertEqual(game.place_settlement(1,6, TERRAIN.GRASS), True)
        self.assertEqual(game.board.resulting_board()[3][7], 't')
        #print(game.board)

    def test_tavernmoves(self):
        game = Game(4)
        #fix quadrants
        game.board.board_env = game.board.joinquadrants(["ORACLE", "PADDOCK", "HARBOR", "FARM"], [False] * 4)
        overlay_terrain(game.board)
        moves = game.board.getpossibletavernmove(self.players[0])
        moves.update(game.board.getpossibletavernmove(self.players[1]))
        moves.update(game.board.getpossibletavernmove(self.players[2]))
        moves.update(game.board.getpossibletavernmove(self.players[3]))
        #game.board.print_selection(moves)
        self.assertEqual(len(moves), 8)

    def test_paddockmoves(self):
        game = Game(4)
        #fix quadrants
        game.board.board_env = game.board.joinquadrants(["ORACLE", "PADDOCK", "HARBOR", "FARM"], [False] * 4)
        overlay_terrain(game.board)
        moves = game.board.getpossiblepaddockmove(game.players[0], 1, 5)
        #game.board.print_selection(moves)
        self.assertEqual(len(moves), 2)
        moves = game.board.getpossiblepaddockmove(game.players[3], 7, 3)
        #game.board.print_selection(moves)
        self.assertEqual(len(moves), 4)

    def test_mixed_board_rule(self):
        set_mixed(self.board)
        players = [ Player(ind) for ind in ["1", "2"] ]
        rules = Rules(self.board, [CARDRULES.WORKER, CARDRULES.FISHERMEN, CARDRULES.HERMITS])
        score_out = rules.score(players)
        self.assertEqual(sum(score_out), 15)
        #print(score_out)
        #print(rules.player_score_per_rule)

    def _actions_to_list(self, game : Game):
        move_options = []
        actions = game.actionstomoves()
        array_index = 0
        for action, rows in actions.items():
            for row_i, row in enumerate(rows):
                if type(row) == int:
                    row = [row]
                for col_i, col in enumerate(row):
                    if col >= 1:
                        move_options.append([action, row_i, col_i])
                        array_index += 1

        return move_options

    def test_randomplay1(self):
        if self.num_games_selfplay <= 0:
            return
        score_sum = [0, 0]
        for _ in range(self.num_games_selfplay):
            fixed_quadrants = ["ORACLE", "PADDOCK", "HARBOR", "FARM"]
            fixed_rules = [CARDRULES.MINERS, CARDRULES.FISHERMEN, CARDRULES.WORKER]
            rotation = [False] * 4
            #only two players
            game = Game(2, fixed_quadrants, rotation, fixed_rules)

            while not game.done:
                # random choise
                action = random.choice(self._actions_to_list(game))
                self.assertEqual(game.singlestepmove(*action), True)
            
            for i, player in enumerate(game.players):
                score_sum[i] += player.score

        player1, player2 = score_sum[0]/self.num_games_selfplay, score_sum[1]/self.num_games_selfplay
        
        print("Average random game score: 1. {:.1f} 2. {:.1f}".format(player1, player2))

        self.assertAlmostEqual(player1, 30, delta=5)
        self.assertAlmostEqual(player2, 30, delta=5)

    def test_randomplay2(self):
        if self.num_games_selfplay <= 0:
            return
        player_cnt = 2
        score_sum = [0] * player_cnt
        for _ in range(self.num_games_selfplay):
            fixed_quadrants = ["ORACLE", "PADDOCK", "HARBOR", "FARM"]
            fixed_rules = [CARDRULES.KNIGHTS, CARDRULES.FARMERS, CARDRULES.LOARDS]
            rotation = [False] * 4
            #only two players
            game = Game(2, fixed_quadrants, rotation, fixed_rules)

            while not game.done:
                # random choise
                action = random.choice(self._actions_to_list(game))
                self.assertEqual(game.singlestepmove(*action), True)
            
            for i, player in enumerate(game.players):
                score_sum[i] += player.score

        player1, player2 = score_sum[0]/self.num_games_selfplay, score_sum[1]/self.num_games_selfplay
        
        print("Average random game score: 1. {:.1f} 2. {:.1f}".format(player1, player2))

        self.assertAlmostEqual(player1, 51, delta=5) 
        self.assertAlmostEqual(player2, 51, delta=5) 

    def test_randomplay3(self):
        if self.num_games_selfplay <= 0:
            return
        player_cnt = 2
        score_sum = [0] * player_cnt
        for _ in range(self.num_games_selfplay):
            fixed_quadrants = ["ORACLE", "PADDOCK", "HARBOR", "FARM"]
            fixed_rules = [CARDRULES.MINERS, CARDRULES.FISHERMEN, CARDRULES.WORKER]
            rotation = [False] * 4
            #only two players
            game = Game(2, fixed_quadrants, rotation, fixed_rules)

            while not game.done:
                # random choise
                action = random.choice(self._actions_to_list(game))
                self.assertEqual(game.singlestepmove(*action), True)
            
            for i, player in enumerate(game.players):
                score_sum[i] += player.score

        player1, player2 = score_sum[0]/self.num_games_selfplay, score_sum[1]/self.num_games_selfplay
        
        print("Average random game score: 1. {:.1f} 2. {:.1f}".format(player1, player2))

        self.assertAlmostEqual(player1, 30, delta=5) 
        self.assertAlmostEqual(player2, 30, delta=5)

    def test_randomplay4(self):
        if self.num_games_selfplay <= 0:
            return
        player_cnt = 5
        score_sum = [0] * player_cnt
        for _ in range(self.num_games_selfplay):
            #fixed_quadrants = ["ORACLE", "PADDOCK", "HARBOR", "FARM"]
            #fixed_rules = [CARDRULES.MINERS, CARDRULES.FISHERMEN, CARDRULES.WORKER]
            #only two players
            game = Game(player_cnt)

            while not game.done:
                # random choise
                action = random.choice(self._actions_to_list(game))
                self.assertEqual(game.singlestepmove(*action), True)
            
            for i, player in enumerate(game.players):
                score_sum[i] += player.score

        score_sum = [score_sum[i] / self.num_games_selfplay for i, x in enumerate(game.players)]
        
        print("Average random game score: ", score_sum)

    def test_deepcopy(self):
        player_cnt = 2
        move_copy_env = 30

        game = Game(player_cnt, deterministic=True)
        gamecopy = None
        move_cnt = 0
        while not game.done:
            # random choise
            action = random.choice(self._actions_to_list(game))
            self.assertEqual(game.singlestepmove(*action), True)
            if gamecopy != None:
                step = gamecopy.singlestepmove(*action)
                self.assertEqual(step, True)
                #current move should bring equal gold to players
                self.assertEqual(game.score(), gamecopy.score())

            if move_copy_env == move_cnt:
                game_state = game.gamestate_to_dict()
                gamecopy = deepcopy(game)
                game.dict_to_gamestate(game_state)
            move_cnt += 1

    def test_saverestore(self):
        player_cnt = 2
        move_copy_env = 30

        game = Game(player_cnt, deterministic=True)
        gamecopy = None
        move_cnt = 0
        while not game.done:
            # random choise
            action = random.choice(self._actions_to_list(game))
            self.assertEqual(game.singlestepmove(*action), True)
            if gamecopy != None:
                step = gamecopy.singlestepmove(*action)
                self.assertEqual(step, True)
                #current move should bring equal gold to players
                self.assertEqual(game.score(), gamecopy.score())

            if move_copy_env == move_cnt:
                game.save("game_save.ini")
                gamecopy = deepcopy(game)
                game = Game.load("game_save.ini")
            move_cnt += 1
    
    def test_display_randomboards(self):
        return
        #how to check random boards? Do it manually 
        for _ in range(3):
            game = Game(2)
            print(game.board)

    def test_towermoves(self):
        fixed_quadrants = ["ORACLE", "PADDOCK", "HARBOR", "FARM"]
        rotation = [False] * 4
        game = Game(2, fixed_quadrants, rotation)
        moves = game.board.getpossibletowermove(game.player)
        #game.board.print_selection(moves)
        self.assertEqual(len(moves), 55)

    def test_rulecards(self):
        #TODO: add checks for rule 9 and rule 10 later
        set_default_terrain(self.board)
        #print(self.board)

        rule_list = [
                        [1, 3, 7],
                        [1, 3, 8],
                        [1, 4, 7],
                        [1, 4, 8],
                        [1, 5, 7],
                        [1, 5, 8],
                        [1, 6, 7],
                        [1, 6, 8],
                        [2, 3, 7],
                        [2, 3, 8],
                        [2, 4, 7],
                        [2, 4, 8],
                        [2, 5, 7],
                        [2, 5, 8],
                        [2, 6, 7],
                        [2, 6, 8],
                    ]

        score = [
                    [52, 46, 43, 62],
                    [49, 51, 45, 35],
                    [43, 37, 44, 61],
                    [40, 42, 46, 34],
                    [57, 61, 45, 75],
                    [54, 66, 47, 48],
                    [57, 25, 48, 84],
                    [54, 30, 50, 57],
                    [52, 34, 59, 56],
                    [49, 39, 61, 29],
                    [43, 25, 60, 55],
                    [40, 30, 62, 28],
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
    #profile perfomance with "python -m cProfile tests.py"
    #tests = TestRules()
    #tests.test_randomplay1()

    #run all unit tests
    unittest.main()

