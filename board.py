import math
from enum import Enum, unique

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

@unique
class BOARDSECTIONS(Enum):
    NONE = 0
    ORACLE = 1
    FARM = 2
    OASIS = 3
    TOWER = 4
    TAVERN = 5
    BARN = 6
    HARBOR = 7
    PADDOCK= 8

    @staticmethod
    def list():
        return list(BOARDSECTIONS)

@unique
class TERRAIN(Enum):
    NONE = ' '
    GRASS = 'G'
    FLOWER = 'B' #german "blume"
    FOREST = 'F'
    CANYON = 'S' #german "stein"
    DESERT = 'D'

    @staticmethod
    def list():
        return list(TERRAIN)

@unique
class SPECIALLOCATION(Enum):
    NONE = ' '
    WATER = 'W'
    MOUNTAIN = 'M'
    CASTLE = 'C'
    TOWNFULL = 'T'
    TOWNHALF = 't'
    TOWNEMPTY = 'X'

    @staticmethod
    def list():
        return list(SPECIALLOCATION)

@unique
class CARDRULES(Enum):
    CASTLE = 0
    DICOVERES = 1
    KNIGHTS = 2
    FISHERMEN = 3
    MINERS = 4
    LOARDS = 5
    FARMERS = 6
    HERMITS = 7
    CITIZENS = 8
    WORKER = 9

    @staticmethod
    def list():
        return list(CARDRULES)

class Board:

    def __init__(self):
        self.max_players = 5
        self.playerlist = [str(x) for x in range(1, self.max_players + 1)]
        self.board_env = [row.split() for row in board_env.strip().split("\n")]
        self.board_settlements = [row.split() for row in board_settlements.strip().split("\n")]

    def is_env(self, row, col, env):
        return self.board_env[row][col] == env

    def resulting_board(self):
        board_merged = [row[:] for row in self.board_env]
        for i_row, row in enumerate(self.board_settlements):
            for i_col, house in enumerate(row):
                if house in self.playerlist:
                    board_merged[i_row][i_col] = house

        return board_merged

    def quadrants(self):
        cb = self.resulting_board()
        return [[cb[i][0:10] for i in range(0,10)], [cb[i][0:10] for i in range(10,20)], [cb[i][10:20] for i in range(0,10)], [cb[i][10:20] for i in range(10,20)]]

    def __str__(self):
        board = self.resulting_board()
        str_out = ""
        for i, row in enumerate(board):
            if i % 2 == 1:
                str_out += " "

            str_out += " " + " ".join(row) + "\n"
        return str_out[:-1]

    #source is https://codegolf.stackexchange.com/questions/44485/score-a-game-of-kingdom-builder
    @staticmethod
    def neighbours(row, col):
        neighbour_set = set()
        
        for dr, dc in {(-1,-1), (-1,0), (0,-1), (0,1), (1,-1), (1,0)}:
            neighbour_set.add((row + dr, col + dc + (1 if dr != 0 and row%2 == 1 else 0)))

        return {(r,c) for r,c in neighbour_set if 20>r>-1 and 20>c>-1}

    @staticmethod
    def is_neighbour(board, row, col, object1, object2):
        return board[row][col] == object1 and object2 in {board[r][c] for r,c in Board.neighbours(row, col)}

class Rules:

    def __init__(self, board : Board):
        self.board = board
        self.rule_set = CARDRULES.list()
        self.rules = [CARDRULES.CASTLE, self.rule_set[1], self.rule_set[5], self.rule_set[7]]
        #self.rules = [self.rule_set[1]]

    def score(self, player_list):
        player_score = [0.0] * len(player_list)

        quadrant_houses_per_player = [ [0]*len(player_list) for i in range(4)]

        board_copy_score_7 = self.board.resulting_board()
        board_copy = self.board.resulting_board()

        quadrants = self.board.quadrants()

        for i, player in enumerate(player_list):

            ### row and column based counting
            max_sattlements_row = 0
            max_sattlements_group = 0
            for row in range(20):
                max_sattlements_row_current = 0
                if CARDRULES.DICOVERES in self.rules:
                    player_score[i] += (player in board_copy[row])
                for col in range(20):
                    max_sattlements_row_current += (board_copy[row][col] == player)
                    if CARDRULES.CASTLE in self.rules:
                        player_score[i] += 3 * Board.is_neighbour(board_copy, row, col, SPECIALLOCATION.CASTLE.value, player)
                    if CARDRULES.WORKER in self.rules:
                        player_score[i] += Board.is_neighbour(board_copy, row, col, player, SPECIALLOCATION.CASTLE.value)
                        player_score[i] += Board.is_neighbour(board_copy, row, col, player, SPECIALLOCATION.TOWNFULL)
                        player_score[i] += Board.is_neighbour(board_copy, row, col, player, SPECIALLOCATION.TOWNHALF)
                        player_score[i] += Board.is_neighbour(board_copy, row, col, player, SPECIALLOCATION.TOWNEMPTY)
                    if CARDRULES.FISHERMEN in self.rules:
                        player_score[i] += (Board.is_neighbour(board_copy, row, col, player, SPECIALLOCATION.WATER.value) and not self.board.is_env(row,col, 'W'))
                    if CARDRULES.MINERS in self.rules:
                        player_score[i] += Board.is_neighbour(board_copy, row, col, player, SPECIALLOCATION.MOUNTAIN.value)
                    is_single_group, num_of_sattlements = self.rule_7_score(player, board_copy_score_7, row, col, 0)
                    if num_of_sattlements > max_sattlements_group:
                        max_sattlements_group = num_of_sattlements
                    if CARDRULES.HERMITS in self.rules:
                        player_score[i] += is_single_group

                if max_sattlements_row_current > max_sattlements_row:
                    max_sattlements_row =  max_sattlements_row_current
            
            
            if CARDRULES.KNIGHTS in self.rules:
                player_score[i] += max_sattlements_row * 2
            if CARDRULES.CITIZENS in self.rules:
                player_score[i] += max_sattlements_group // 2

            if CARDRULES.LOARDS in self.rules or CARDRULES.FARMERS in self.rules:
                ## quadrant based counting
                for index_qua, quadrant in enumerate(quadrants):
                    for row in range(10):
                        for col in range(10):
                            quadrant_houses_per_player[i][index_qua] += (quadrant[row][col] == player)

                if CARDRULES.FARMERS in self.rules:
                    player_score[i] += min(quadrant_houses_per_player[i]) * 3

        if CARDRULES.LOARDS in self.rules:
            tran_ply_qua = [ list(e) for e in zip(*quadrant_houses_per_player)]
            for qua in tran_ply_qua:

                for gold in [12, 6]:
                    max_houses = max(qua)
                    if max_houses == 0:
                        continue
                    for player, houses in enumerate(qua):
                        if max_houses == houses:
                            player_score[player] += gold
                            qua[player] = 0

        return player_score

    def rule_7_score(self, player, board_modify, row, col, counter):
        is_char = (board_modify[row][col] == player)
        board_modify[row][col] = "" if is_char else board_modify[row][col]

        if is_char:
            counter += 1
            for neighbour in self.board.neighbours(row, col):
                _, counter = self.rule_7_score(player, board_modify, *neighbour, counter)

        return is_char, counter
        

board = Board()

rules = Rules(board)

print(board)


print(rules.score(["1", "2", "3", "4"]))