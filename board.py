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
    
    @staticmethod
    def list_values():
        return [e.value for e in TERRAIN]


@unique
class SPECIALLOCATION(Enum):
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


class Player:
    def __init__(self, index:str):
        self.takecard()
        self.player_index = index
        self.starter = False # player starts the round
        self._score = 0
        self.settlements = 40
        self.towns = []

    def takecard(self):
        self.current_card = random.choice(TERRAIN.list())
        return self.current_card

    def addTown(self, town : BOARDSECTIONS):
        self.towns.append(town)

    def setStarter(self):
        self.starter = True

    def isStarter(self):
        return self.starter

    def decrement_settlement(self):
        self.settlements -= 1
        if self.settlements < 0:
            raise ValueError()

    def increment_settlement(self):
        self.settlements += 1
        if self.settlements > 40:
            raise ValueError()

    def isfinished(self):
        return self.settlements == 0


    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, score):
        self._score = score

    def __str__(self):
        return self.player_index

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
            self.quadrant_order = random.sample(self.env_quadrants["quadrants"], 4)
        else:
            self.quadrant_order = quadrant_name_list
        #TODO: random rotation
        qua = [self.env_quadrants[x] for x in self.quadrant_order]
        board = []
        for row in range(10):
            board.append(qua[0][row] + qua[1][row])
        for row in range(10):
            board.append(qua[2][row] + qua[3][row])
        return board

    def town_to_boardsection(self, row, col):
        if self.board_env[row][col] not in [SPECIALLOCATION.TOWNHALF.value, SPECIALLOCATION.TOWNFULL.value]:
            return None
        ind = (row // 10) * 2  + (col // 10)
        return BOARDSECTIONS[self.quadrant_order[ind]]
        

    @property
    def env(self):
        return self.board_env

    def is_env(self, row, col, env, board = None):
        if board:
            return board[row][col] == env
        else:
            return self.board_env[row][col] == env

    def resulting_board(self):
        board_merged = [row[:] for row in self.board_env]
        for i_row, row in enumerate(self.board_settlements):
            for i_col, house in enumerate(row):
                if house in self.playerlist:
                    board_merged[i_row][i_col] = house

        return board_merged

    def place_settlement(self, player : Player, row, col, env_rule):
        place_options = self.getpossiblemove(player, env_rule)
        if (row, col) in place_options:
            self.board_settlements[row][col] = str(player)
            return True
        return False

    def grab_town(self, row, col):
        if self.board_env[row][col] == SPECIALLOCATION.TOWNFULL.value:
            self.board_env[row][col] = SPECIALLOCATION.TOWNHALF.value
        elif self.board_env[row][col] == SPECIALLOCATION.TOWNHALF.value:
            self.board_env[row][col] = SPECIALLOCATION.TOWNEMPTY.value
        else:
            raise ValueError()

    def reset_settlement(self, player : Player, row, col):
        if self.board_settlements[row][col] == str(player):
            self.board_settlements[row][col] = ' '
            return True
        return False

    def getpossiblepaddockmove(self, player, row, col):
        board = self.resulting_board()
        moves = set()
        # is player settlement not in field?
        if self.board_settlements[row][col] != str(player):
            return moves

        for dr, dc in {(0,-2), (0,2), (-2,-1), (-2,1), (2,-1), (2,1)}:
            moves.add((row + dr, col + dc + (1 if dr != 0 and row%2 == 1 else 0)))
        moves = {(r,c) for r,c in moves if 20>r>-1 and 20>c>-1 and board[r][c] in TERRAIN.list_values() }
        
        return moves

    def getpossiblemove(self, player : Player, env_field):
        if type(env_field) != str:
            env_field = env_field.value # switch from enum to string representation

        board = self.resulting_board()
        fields_in_range = set()
        fields_free = set()
        #check if settlements are in range of the given field
        for row in range(20):
            for col in range(20):
                if self.is_env(row, col, env_field, board):
                    fields_free.add((row, col))
                if str(player) == board[row][col]:
                    for neighbour in self.neighbours(row, col):
                        if self.is_env(*neighbour, env_field, board):
                            fields_in_range.add(neighbour)

        if len(fields_in_range) > 0:
            return fields_in_range
        else:
            return fields_free

    def quadrants(self):
        cb = self.resulting_board()
        return [[cb[i][0:10] for i in range(0,10)], [cb[i][0:10] for i in range(10,20)], [cb[i][10:20] for i in range(0,10)], [cb[i][10:20] for i in range(10,20)]]


    def board_with_selection(self, field_set = None):
        board = self.resulting_board()
        str_out = "\n     "
        for i in range(20):
            str_out += " {:02d} ".format(i)
        str_out += "\n"
        for i_row, row in enumerate(board):
            if i_row % 2:
                str_out += "{:02d}  ".format(i_row)
            else:
                str_out += "{:02d}".format(i_row)
            for i_col, col in enumerate(row):
                col_delimit = [' ', ' ', ' ']
                if field_set != None:
                    if i_row % 2:
                        if (i_row, i_col) in field_set:
                            col_delimit[2] = '|'
                        if (i_row, i_col - 1) in field_set:
                            col_delimit[0] = '|'
                        if (i_row + 1, i_col) in field_set:
                            col_delimit[1] = '_'
                        if (i_row - 1, i_col) in field_set:
                            col_delimit[1] = '-'
                    else:
                        if (i_row, i_col) in field_set:
                            col_delimit[2] = '|'
                        if (i_row, i_col - 1) in field_set:
                            col_delimit[0] = '|'
                        if (i_row + 1, i_col - 1) in field_set:
                            col_delimit[1] = '_'
                        if (i_row - 1, i_col - 1) in field_set:
                            col_delimit[1] = '-'

                str_out += "".join(col_delimit) + col

            str_out += "\n"

        return str_out[:-1]

    def print_selection(self, field_set = None):
        print(self.board_with_selection(field_set))

    def __str__(self):
        return self.board_with_selection(None)

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
        return (object1 == None or board1[row][col] == object1) and object2 in {board1[r][c] for r,c in Board.neighbours(row, col)}

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



class Game:
    def __init__(self, num_players : int):
        #init random quadrants from folder quadrants
        self.board = Board("quadrants")
        #init random rules cards
        self.rules = Rules(self.board)
        #init players
        self.players = [ Player(str(ind)) for ind in range(1, num_players + 1) ]
        #set random start player
        self.current_player = random.randrange(0, num_players)
        self.players[self.current_player].setStarter()

    @property
    def player(self):
        return self.players[self.current_player]

    def nextPlayer(self):
        self.current_player += 1
        if len(self.players) >= self.current_player:
            self.current_player = 0

    def place_settlement(self, row, col, env_rule):
        if self.board.place_settlement(self.player, row, col, env_rule):
            self.player.decrement_settlement()
            town, tcoord = self.checkTown(row, col)
            if town != None:
                self.board.grab_town(*tcoord)
                self.player.addTown(town)
            return True

        return False

    def checkTown(self, row, col):
        nei_list = self.board.neighbours(row, col)
        for loc in nei_list:
            board = self.board.resulting_board()
            board[row][col] = ' ' # delete current settlement temporary 
            #settlement placed next to town with left quests - no settlement could be next to two towns
            if board[loc[0]][loc[1]] in [SPECIALLOCATION.TOWNFULL.value, SPECIALLOCATION.TOWNHALF.value]:
                #check if no other settlement is placed next to 
                if not self.board.is_neighbour(board, None, loc[0], loc[1], None, str(self.player)):
                    return self.board.town_to_boardsection(*loc), loc

        return None, None

    def endmove(self):
        if self.player.isfinished():
            score = self.rules.score(self.players)
            print(score)

game = Game(4)

print(game.board)
print(game.rules.score(game.players))
print(game.players[0].takecard())