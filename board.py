import random
import os

from player import Player
from quadrants import quadrants as quadrants_dict
from accessories import CARDRULES, TERRAIN, SPECIALLOCATION, BOARDSECTIONS


class Board:

    def __init__(self, quadrants : list = []):
        self.max_players = 5
        self.playerlist = [str(x) for x in range(1, self.max_players + 1)]
        self.board_settlements = [ ['0']*20 for i in range(20)]
        self.board_changed = True
        self.load_quadrants()
        self.board_env = self.joinquadrants(quadrants)
        self.generatetowerfields() #precompute

    def generatetowerfields(self):
        self.gen_tower_field = set()
        for row in range(20):
            for col in [0,19]:
                self.gen_tower_field.add((row, col))
        for row in [0,19]:
            for col in range(1,19):
                self.gen_tower_field.add((row, col))

    def load_quadrants(self):
        self.env_quadrants = {"quadrants" : []}
        quadrant_names = [x.name for x in BOARDSECTIONS.list()]
        for qua_name, raw_board in quadrants_dict.items():
            if qua_name in quadrant_names:
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

    def is_env(self, row, col, env = None, board = None):
        env_list = [env]
        #if env none - all env are checked (tower moves)
        if env == None:
            env_list = TERRAIN.list_values()
        if board:
            return board[row][col] in env_list
        else:
            return self.board_env[row][col] in env_list

    def resulting_board(self, force_refresh = False):
        if self.board_changed or force_refresh:
            self.board_merged = [row[:] for row in self.board_env]
            for i_row, row in enumerate(self.board_settlements):
                for i_col, house in enumerate(row):
                    if house in self.playerlist:
                        self.board_merged[i_row][i_col] = house
        
        self.board_changed = False
        return [row[:] for row in self.board_merged] # return a copy

    def grab_town(self, row, col):
        if self.board_env[row][col] == SPECIALLOCATION.TOWNFULL.value:
            self.board_env[row][col] = SPECIALLOCATION.TOWNHALF.value
        elif self.board_env[row][col] == SPECIALLOCATION.TOWNHALF.value:
            self.board_env[row][col] = SPECIALLOCATION.TOWNEMPTY.value
        else:
            raise ValueError()

    def place_settlement(self, player : Player, row, col, env_rule):
        place_options = self.getpossiblemove(player, env_rule)
        if (row, col) in place_options:
            self.board_settlements[row][col] = str(player)
            self.board_changed = True
            return True
        return False

    def reset_settlement(self, player : Player, row, col):
        if self.board_settlements[row][col] == str(player):
            self.board_settlements[row][col] = '0'
            self.board_changed = True
            return True
        return False

    def move_settlement(self, player : Player, row_from, col_from, row_to, col_to):
        board = self.resulting_board()
        possible_env_list = TERRAIN.list_values() + [SPECIALLOCATION.WATER.value]
        if board[row_from][col_from] != str(player):
            return False
        if board[row_to][col_to] in possible_env_list:
            self.board_settlements[row_to][col_to] = str(player)
            self.board_settlements[row_from][col_from] = '0'
            self.board_changed = True
            return True
        return False

    def getpossibletavernmove(self, player):
        board = self.resulting_board()
        moves = set()

        tavern_sets =  {    0: #"even":
                            {   "neighbours": [
                                    #horizonal
                                    set({(0,1),(0,2)}),
                                    set({(0,-1),(0,-2)}),
                                    #diagonal right
                                    set({(1,0),(2,1)}),
                                    set({(-1,0),(-2,1)}),
                                    #diagonal left
                                    set({(1,-1),(2,-1)}),
                                    set({(-1,-1),(-2,-1)}),
                                ],
                                "options": [
                                    #horizonal
                                    (0,3),
                                    (0,-3),
                                    #diagonal right
                                    (3, 1),
                                    (-3,1),
                                    #diagonal left
                                    (3, -2),
                                    (-3,-2),
                                ]
                            }, 1: #"uneven":
                            { "neighbours": [
                                    #horizonal - same like even - do not check again
                                    set({(0,1),(0,2)}),
                                    set({(0,-1),(0,-2)}),
                                    #diagonal right
                                    set({(1,1),(2,1)}),
                                    set({(-1,1),(-2,1)}),
                                    #diagonal left
                                    set({(1,0),(2,-1)}),
                                    set({(-1,0),(-2,-1)}),
                                ],
                                "options": [
                                    #horizonal
                                    (0,3),
                                    (0,-3),
                                    #diagonal right
                                    (3, 2),
                                    (-3,2),
                                    #diagonal left
                                    (3, -1),
                                    (-3,-1),
                                ]
                            }
                        }

        for row in range(20):
            for col in range(20):
                if board[row][col] != str(player):
                    continue
                comp_set = tavern_sets[row%2]
                for i, neighbour in enumerate(comp_set["neighbours"]):
                    match = True
                    try:
                        for dr, dc in neighbour:
                                if board[row + dr][col + dc] != str(player):
                                    match = False
                                    break
                        
                        res_row = row + comp_set["options"][i][0]
                        res_col = col + comp_set["options"][i][1]
                        if res_row < 0 or res_row > 19 or res_col < 0 or res_col > 19:
                            continue
                        if match and board[res_row][res_col] in TERRAIN.list_values():
                            moves.add((res_row, res_col))
                    except:
                        pass
        
        return moves

    def getpossiblepaddockmove(self, player, row, col):
        board = self.resulting_board()
        moves = set()
        # is player settlement not in field?
        if self.board_settlements[row][col] != str(player):
            return moves

        for dr, dc in {(0,-2), (0,2), (-2,-1), (-2,1), (2,-1), (2,1)}:
            moves.add((row + dr, col + dc ))
        moves = {(r,c) for r,c in moves if 20>r>-1 and 20>c>-1 and board[r][c] in TERRAIN.list_values() }
        
        return moves

    def getpossibletowermove(self, player):
        board = self.resulting_board()

        fields_in_range = set()
        fields_free = set()
        #check if settlements are in range of the given field
        for (row, col) in self.gen_tower_field:
            if self.is_env(row, col, None, board):
                fields_free.add((row, col))
            nei = Board.neighbours(row, col)
            for n in nei:
                if board[n[0]][n[0]] == str(player):
                    fields_in_range.add((row,col))

        if len(fields_in_range) > 0:
            return fields_in_range
        else:
            return fields_free

    def hassettlement(self, player, row, col):
        return self.board_settlements[row][col] == str(player)

    # use blacklist to not return neighbours of a selected settlement for moving options (like harbor)
    def getpossiblemove(self, player : Player, env_field, coord_blacklist: tuple = None):
        if type(env_field) != str:
            env_field = env_field.value # switch from enum to string representation

        board = self.resulting_board()
        if coord_blacklist != None:
            board[coord_blacklist[0]][coord_blacklist[1]] = self.board_env[coord_blacklist[0]][coord_blacklist[1]] #blacklist
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
        str_out = "{:^40}{:^40}\n".format(self.quadrant_order[0], self.quadrant_order[1])
        str_out += "     "
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

            if i_row % 2:
                str_out += "   {:02d}".format(i_row)
            else:
                str_out += "     {:02d}".format(i_row)
            str_out += "\n"
        str_out += "     "
        for i in range(20):
            str_out += " {:02d} ".format(i)
        str_out += "\n{:^40}{:^40}".format(self.quadrant_order[2], self.quadrant_order[3])
        return str_out

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
