import random

from accessories import CARDRULES, TERRAIN, SPECIALLOCATION, BOARDSECTIONS
from board import Board

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
            max_settlements_row = 0
            max_settlements_group = 0
            for row in range(20):
                max_settlements_row_current = 0
                if CARDRULES.DICOVERES in self.rules:
                    score_per_rule[i][CARDRULES.DICOVERES.value] += (player in board_copy[row])
                for col in range(20):
                    max_settlements_row_current += (board_copy[row][col] == player)
                    if CARDRULES.CASTLE in self.rules:
                        score_per_rule[i][CARDRULES.CASTLE.value] += 3 * Board.is_neighbour(board_copy, None, row, col, SPECIALLOCATION.CASTLE.value, player)
                    if CARDRULES.WORKER in self.rules:
                        score_per_rule[i][CARDRULES.WORKER.value] += Board.is_neighbour(board_copy, None, row, col, player, SPECIALLOCATION.CASTLE.value)
                        score_per_rule[i][CARDRULES.WORKER.value] += Board.is_neighbour(board_copy, None, row, col, player, SPECIALLOCATION.TOWNFULL)
                        score_per_rule[i][CARDRULES.WORKER.value] += Board.is_neighbour(board_copy, None, row, col, player, SPECIALLOCATION.TOWNHALF)
                        score_per_rule[i][CARDRULES.WORKER.value] += Board.is_neighbour(board_copy, None, row, col, player, SPECIALLOCATION.TOWNEMPTY)
                    if CARDRULES.FISHERMEN in self.rules:
                        score_per_rule[i][CARDRULES.FISHERMEN.value] += (Board.is_neighbour(board_copy, self.board.env, row, col, player, SPECIALLOCATION.WATER.value) and not self.board.is_env(row,col, 'W'))
                    if CARDRULES.MINERS in self.rules:
                        score_per_rule[i][CARDRULES.MINERS.value] += Board.is_neighbour(board_copy, self.board.env, row, col, player, SPECIALLOCATION.MOUNTAIN.value)
                    is_single_group, num_of_settlements = self.rule_7_score(player, board_copy_score_7, row, col, 0)
                    if num_of_settlements > max_settlements_group:
                        max_settlements_group = num_of_settlements
                    if CARDRULES.HERMITS in self.rules:
                        score_per_rule[i][CARDRULES.HERMITS.value] += is_single_group

                if max_settlements_row_current > max_settlements_row:
                    max_settlements_row =  max_settlements_row_current
            
            
            if CARDRULES.KNIGHTS in self.rules:
                score_per_rule[i][CARDRULES.KNIGHTS.value] += max_settlements_row * 2
            if CARDRULES.CITIZENS in self.rules:
                score_per_rule[i][CARDRULES.CITIZENS.value] += max_settlements_group // 2

            if CARDRULES.LOARDS in self.rules or CARDRULES.FARMERS in self.rules:
                ## quadrant based counting
                for index_qua, quadrant in enumerate(quadrants):
                    for row in range(10):
                        for col in range(10):
                            quadrant_houses_per_player[i][index_qua] += (quadrant[row][col] == player)

                if CARDRULES.FARMERS in self.rules:
                    score_per_rule[i][CARDRULES.FARMERS.value] += min(quadrant_houses_per_player[i]) * 3

        #quadrant based on settlements from other players
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