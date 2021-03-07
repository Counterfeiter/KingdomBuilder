import random
from enum import Enum, unique
import os

@unique
class BOARDSECTIONS(Enum):
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

    def __init__(self, folderpath):
        self.max_players = 5
        self.playerlist = [str(x) for x in range(1, self.max_players + 1)]
        self.board_settlements = [ [' ']*20 for i in range(20)]
        self.load_quadrants(folderpath)
        self.board_env = self.joinquadrants()

    def load_quadrants(self, foldername):
        self.env_quadrants = {"quadrants" : []}
        quadrant_names = [x.name for x in BOARDSECTIONS.list()]
        for filename in os.listdir(foldername):
            qua_name = os.path.basename(filename)
            if qua_name in quadrant_names:
                with open(os.path.join(foldername,filename), 'r') as file:
                    raw_board = file.read()
                    self.env_quadrants["quadrants"].append(qua_name)
                    self.env_quadrants[qua_name] = [row.split() for row in raw_board.strip().split("\n")]

    def joinquadrants(self, quadrant_name_list : list = []):
        if len(quadrant_name_list) != 4:
            quadrant_name_list = random.sample(self.env_quadrants["quadrants"], 4)
        #TODO: random rotation
        qua = [self.env_quadrants[x] for x in quadrant_name_list]
        board = []
        for row in range(10):
            board.append(qua[0][row] + qua[1][row])
        for row in range(10):
            board.append(qua[2][row] + qua[3][row])
        return board

    @property
    def env(self):
        return self.board_env

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
                str_out += "  "

            str_out += "   " + "   ".join(row) + "\n"
        return str_out[:-1]

    #source is https://codegolf.stackexchange.com/questions/44485/score-a-game-of-kingdom-builder
    @staticmethod
    def neighbours(row, col):
        neighbour_set = set()
        
        for dr, dc in {(-1,-1), (-1,0), (0,-1), (0,1), (1,-1), (1,0)}:
            neighbour_set.add((row + dr, col + dc + (1 if dr != 0 and row%2 == 1 else 0)))

        return {(r,c) for r,c in neighbour_set if 20>r>-1 and 20>c>-1}

    @staticmethod
    def is_neighbour(board1, board2, row, col, object1, object2):
        #FIXME: water points should be compared with env map, because players could be on the water with the harbor
        if board2 == None:
            board2 = board1
        return board1[row][col] == object1 and object2 in {board1[r][c] for r,c in Board.neighbours(row, col)}

class Rules:

    def __init__(self, board : Board, cards: list = []):
        self.board = board
        if len(cards) == 3:
            self.rules = [CARDRULES.CASTLE] + cards
        else:
            self.randomcards()

    def randomcards(self):
        self.rule_set = CARDRULES.list()[1:]
        self.rules = [CARDRULES.CASTLE]
        self.rules += random.sample(self.rule_set, 3)
        return self.rules

    def score(self, player_list : list):
        player_score = [0.0] * len(player_list)

        quadrant_houses_per_player = [ [0]*len(player_list) for i in range(4)]

        score_per_rule = [ [0] * len(CARDRULES) for i in range(len(player_list))]

        board_copy_score_7 = self.board.resulting_board()
        board_copy = self.board.resulting_board()

        quadrants = self.board.quadrants()

        for i, player_class in enumerate(player_list):
            player = str(player_class)
            ### row and column based counting
            max_sattlements_row = 0
            max_sattlements_group = 0
            for row in range(20):
                max_sattlements_row_current = 0
                if CARDRULES.DICOVERES in self.rules:
                    score_per_rule[i][CARDRULES.DICOVERES.value] += (player in board_copy[row])
                for col in range(20):
                    max_sattlements_row_current += (board_copy[row][col] == player)
                    if CARDRULES.CASTLE in self.rules:
                        score_per_rule[i][CARDRULES.CASTLE.value] += 3 * Board.is_neighbour(board_copy, None, row, col, SPECIALLOCATION.CASTLE.value, player)
                    if CARDRULES.WORKER in self.rules:
                        score_per_rule[i][CARDRULES.WORKER.value] += Board.is_neighbour(board_copy, None, row, col, player, SPECIALLOCATION.CASTLE.value)
                        score_per_rule[i][CARDRULES.WORKER.value] += Board.is_neighbour(board_copy, None, row, col, player, SPECIALLOCATION.TOWNFULL)
                        score_per_rule[i][CARDRULES.WORKER.value] += Board.is_neighbour(board_copy, None, row, col, player, SPECIALLOCATION.TOWNHALF)
                        score_per_rule[i][CARDRULES.WORKER.value] += Board.is_neighbour(board_copy, None, row, col, player, SPECIALLOCATION.TOWNEMPTY)
                    if CARDRULES.FISHERMEN in self.rules:
                        score_per_rule[i][CARDRULES.FISHERMEN.value] += (Board.is_neighbour(board_copy, board.env, row, col, player, SPECIALLOCATION.WATER.value) and not self.board.is_env(row,col, 'W'))
                    if CARDRULES.MINERS in self.rules:
                        score_per_rule[i][CARDRULES.MINERS.value] += Board.is_neighbour(board_copy, board.env, row, col, player, SPECIALLOCATION.MOUNTAIN.value)
                    is_single_group, num_of_sattlements = self.rule_7_score(player, board_copy_score_7, row, col, 0)
                    if num_of_sattlements > max_sattlements_group:
                        max_sattlements_group = num_of_sattlements
                    if CARDRULES.HERMITS in self.rules:
                        score_per_rule[i][CARDRULES.HERMITS.value] += is_single_group

                if max_sattlements_row_current > max_sattlements_row:
                    max_sattlements_row =  max_sattlements_row_current
            
            
            if CARDRULES.KNIGHTS in self.rules:
                score_per_rule[i][CARDRULES.KNIGHTS.value] += max_sattlements_row * 2
            if CARDRULES.CITIZENS in self.rules:
                score_per_rule[i][CARDRULES.CITIZENS.value] += max_sattlements_group // 2

            if CARDRULES.LOARDS in self.rules or CARDRULES.FARMERS in self.rules:
                ## quadrant based counting
                for index_qua, quadrant in enumerate(quadrants):
                    for row in range(10):
                        for col in range(10):
                            quadrant_houses_per_player[i][index_qua] += (quadrant[row][col] == player)

                if CARDRULES.FARMERS in self.rules:
                    score_per_rule[i][CARDRULES.FARMERS.value] += min(quadrant_houses_per_player[i]) * 3

        #quadrant based on sattlements from other players
        if CARDRULES.LOARDS in self.rules:
            tran_ply_qua = [ list(e) for e in zip(*quadrant_houses_per_player)]
            for qua in tran_ply_qua:

                for gold in [12, 6]:
                    max_houses = max(qua)
                    if max_houses == 0:
                        continue
                    for player, houses in enumerate(qua):
                        if max_houses == houses:
                            score_per_rule[player][CARDRULES.LOARDS.value] += gold
                            qua[player] = 0

        for i in range(len(player_list)):
            player_list[i].score = sum(score_per_rule[i])
            player_score[i] = sum(score_per_rule[i])

        self.player_score_per_rule = score_per_rule

        return player_score

    def rule_7_score(self, player, board_modify, row, col, counter):
        is_char = (board_modify[row][col] == player)
        board_modify[row][col] = "" if is_char else board_modify[row][col]

        if is_char:
            counter += 1
            for neighbour in self.board.neighbours(row, col):
                _, counter = self.rule_7_score(player, board_modify, *neighbour, counter)

        return is_char, counter

class Player:
    def __init__(self, index:str):
        self.takecard()
        self.player_index = index
        self.starter = False # player starts the round
        self._score = 0

    def takecard(self):
        self.current_card = random.choice(TERRAIN.list())
        return self.current_card

    def setStarter(self):
        self.starter = True

    def isStarter(self):
        return self.starter

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, score):
        self._score = score

    def __str__(self):
        return self.player_index

        

board = Board("quadrants")

rules = Rules(board)

print(rules.randomcards())

players = [ Player(ind) for ind in ["1", "2", "3", "4"] ]

print(board)

print(rules.score(players))

print(players[0].takecard())