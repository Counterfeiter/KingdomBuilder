from enum import Enum, unique
import random
from typing import OrderedDict

from board import Board
from rules import Rules
from player import Player
from accessories import CARDRULES, TERRAIN, SPECIALLOCATION, BOARDSECTIONS
import collections

@unique
class DOACTION(Enum):
    TAKENEWCARD = 0 # if no terrain for the given terrain card left - take a new one - otherwise card is taken after "END" without interaction
    END = 1
    MAINMOVE = 2
    ORACLE = 3
    FARM = 4
    HARBORSELECT = 5
    HARBORSET = 6
    PADDOCKSELECT = 7
    PADDOCKSET = 8
    OASIS = 9
    BARNSELECT = 10
    BARNSET = 11

class Game:
    def __init__(self, num_players : int, quadrants : list = [], rules : list = []):
        # 4 player is orginal... 
        # but in expansion modes you get settlements for a 5th player
        if num_players < 1 or num_players > 5:
            raise ValueError()
        #init random quadrants from folder quadrants
        self.board = Board(quadrants)
        #init random rules cards
        self.rules = Rules(self.board, rules)
        #init players
        self.players = [ Player(str(ind)) for ind in range(1, num_players + 1) ]
        #set random start player
        self.current_player = random.randrange(0, num_players)
        self.players[self.current_player].setStarter()
        self.townstoplay = []
        self.game_done = False
        self.main_move = 3
        self.old_action = None

    @property
    def __version__(self):
        return "0.0.1"

    @property
    def player(self):
        return self.players[self.current_player]

    def nextPlayer(self):
        self.current_player += 1
        if self.current_player >= len(self.players):
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

    def move_settlement(self, row_from, col_from, row_to, col_to):
        if self.board.move_settlement(self.player, row_from, col_from, row_to, col_to):
            # TODO: delete town if leaving all/last settlement(s)
            town, tcoord = self.checkTown(row_to, col_to)
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

    def getcoordinates(self):
        inp = input("Please enter row, col or type abort\n")
        ilist = inp.replace(" ","").split(",")
        if ilist == "abort":
            return None, True
        try:
            row = int(ilist[0])
            col = int(ilist[1])
        except:
            return None, False
        
        return (row, col), False
    
    def checktownplay_possible(self, town):
        return (self.main_move == 3 or self.main_move == 0) and self.player.settlements > 0 and town in self.townstoplay

    def oldactionnoselection(self, pass_if = None):
        return self.old_action == pass_if or not (self.old_action == DOACTION.HARBORSELECT or self.old_action == DOACTION.PADDOCKSELECT)

    def actionstomoves(self):
        # pa = possible actions
        pa = OrderedDict()
        
        pa[DOACTION.TAKENEWCARD] = [[0]]
        pa[DOACTION.END] = [[1]] if self.main_move == 0 or self.player.settlements == 0 else [[0]]
        ### could be done in a loop... but it is a ordered dict, we will leave at as reference
        # for the flattend action mask array
        pa[DOACTION.MAINMOVE] = [ [0]*20 for i in range(20)]
        pa[DOACTION.ORACLE] = [ [0]*20 for i in range(20)]
        pa[DOACTION.FARM] = [ [0]*20 for i in range(20)]
        pa[DOACTION.HARBORSELECT] = [ [0]*20 for i in range(20)]
        pa[DOACTION.HARBORSET] = [ [0]*20 for i in range(20)]
        pa[DOACTION.PADDOCKSELECT] = [ [0]*20 for i in range(20)]
        pa[DOACTION.PADDOCKSET] = [ [0]*20 for i in range(20)]
        pa[DOACTION.OASIS] = [ [0]*20 for i in range(20)]
        

        if self.main_move > 0 and self.player.settlements > 0:
            moves = self.board.getpossiblemove(self.player, self.player.card)
            for coord in moves:
                pa[DOACTION.MAINMOVE][coord[0]][coord[1]] = 1
            #check if player could take a new card 
            if len(moves) <= 0:
                pa[DOACTION.TAKENEWCARD][0] = 1

        if self.checktownplay_possible(BOARDSECTIONS.FARM):
            moves = self.board.getpossiblemove(self.player, TERRAIN.GRASS)
            for coord in moves:
                pa[DOACTION.FARM][coord[0]][coord[1]] = 1

        if self.checktownplay_possible(BOARDSECTIONS.ORACLE):
            moves = self.board.getpossiblemove(self.player, self.player.card)
            for coord in moves:
                pa[DOACTION.ORACLE][coord[0]][coord[1]] = 1
            if len(moves) <= 0:
                pa[DOACTION.TAKENEWCARD][0] = 1

        if self.checktownplay_possible(BOARDSECTIONS.PADDOCK) and self.oldactionnoselection():
            moves = self.board.getpossiblemove(self.player, str(self.player))
            for coord in moves:
                pa[DOACTION.PADDOCKSELECT][coord[0]][coord[1]] = 1
        
        if self.checktownplay_possible(BOARDSECTIONS.PADDOCK):
            if self.old_action == DOACTION.PADDOCKSELECT:
                moves = self.board.getpossiblepaddockmove(self.player, *self.select_coord)
                for coord in moves:
                    pa[DOACTION.PADDOCKSET][coord[0]][coord[1]] = 1
        
        if self.checktownplay_possible(BOARDSECTIONS.HARBOR) and self.oldactionnoselection():
            moves = self.board.getpossiblemove(self.player, str(self.player))
            for coord in moves:
                pa[DOACTION.HARBORSELECT][coord[0]][coord[1]] = 1
        
        if self.checktownplay_possible(BOARDSECTIONS.HARBOR):
            if self.old_action == DOACTION.HARBORSELECT:
                moves = self.board.getpossiblemove(self.player, SPECIALLOCATION.WATER, self.select_coord)
                for coord in moves:
                    pa[DOACTION.HARBORSET][coord[0]][coord[1]] = 1

        if self.checktownplay_possible(BOARDSECTIONS.OASIS):
            moves = self.board.getpossiblemove(self.player, TERRAIN.DESERT)
            for coord in moves:
                pa[DOACTION.OASIS][coord[0]][coord[1]] = 1

        if self.checktownplay_possible(BOARDSECTIONS.BARN) and self.oldactionnoselection():
            moves = self.board.getpossiblemove(self.player, str(self.player))
            for coord in moves:
                pa[DOACTION.BARNSELECT][coord[0]][coord[1]] = 1
        
        if self.checktownplay_possible(BOARDSECTIONS.BARN):
            if self.old_action == DOACTION.BARNSELECT:
                moves = self.board.getpossiblemove(self.player, self.player.card, *self.select_coord)
                for coord in moves:
                    pa[DOACTION.BARNSET][coord[0]][coord[1]] = 1

        return pa

    #controlled by an rl agent?
    def singlestepmove(self, action : DOACTION, row, col):
        res = self._singlestepmove(action, row, col)
        if res:
            #store old action if move was valid
            self.old_action = action
        return res

    def _singlestepmove(self, action : DOACTION, row, col):
        moves = None
        if action == DOACTION.END:
            if self.main_move == 0 or self.player.settlements == 0:
                self.endmove()
                self.startmove()
                return True
            else:
                return False

        if action == DOACTION.TAKENEWCARD:
            moves = self.board.getpossiblemove(self.player, self.player.card)
            #TODO: check also if any move left
            if len(moves) <= 0:
                self.player.takecard()
                return True
            return False

        # nothing to do
        if not ((len(self.townstoplay) > 0 or self.main_move > 0) and self.player.settlements != 0):
            return False
        #main move and no settlements to place?
        if action == DOACTION.MAINMOVE and self.main_move <= 0:
            return False
        #main move played in a sequence?
        if self.main_move < 3 and self.main_move > 0 and action != DOACTION.MAINMOVE:
            return False

        if action == DOACTION.MAINMOVE:
            if self.place_settlement(row, col, self.player.card):
                self.main_move -= 1
                return True
        elif action == DOACTION.FARM and BOARDSECTIONS.FARM in self.townstoplay:
            if self.place_settlement(row, col, TERRAIN.GRASS):
                self.townstoplay.remove(BOARDSECTIONS.FARM)
                return True
        elif action == DOACTION.ORACLE and BOARDSECTIONS.ORACLE in self.townstoplay:
            if self.place_settlement(row, col, self.player.card):
                self.townstoplay.remove(BOARDSECTIONS.ORACLE)
                return True
        elif action == DOACTION.HARBORSELECT and BOARDSECTIONS.HARBOR in self.townstoplay:
            if self.board.hassettlement(self.player, row, col):
                self.select_coord = (row, col)
                return True
        elif action == DOACTION.HARBORSET and self.old_action == DOACTION.HARBORSELECT:
            moves = self.board.getpossiblemove(self.player, SPECIALLOCATION.WATER, self.select_coord)
            if (row, col) not in moves:
                return False
            if self.board.move_settlement(self.player, *self.select_coord, row, col):
                self.townstoplay.remove(BOARDSECTIONS.HARBOR)
                return True
        elif action == DOACTION.PADDOCKSELECT and BOARDSECTIONS.PADDOCK in self.townstoplay:
            if self.board.hassettlement(self.player, row, col):
                self.select_coord = (row, col)
                return True
        elif action == DOACTION.PADDOCKSET and self.old_action == DOACTION.PADDOCKSELECT:
            moves = self.board.getpossiblepaddockmove(self.player, *self.select_coord)
            if (row, col) not in moves:
                return False
            if self.board.move_settlement(self.player, *self.select_coord, row, col):
                self.townstoplay.remove(BOARDSECTIONS.PADDOCK)
                return True
        #debug board
        if moves:
            self.board.print_selection(moves)
        else:
            print(str(self.board))
        return False

    @property
    def done(self):
        return self.game_done
            
    def startmove(self):
        #end game if starter is reached an any player is finished
        fin = [x.isfinished() for x in self.players]
        if self.player.isStarter() and True in fin:
            score = self.rules.score(self.players)
            print("Game ends with score: ", score)
            self.game_done = True
            return False

        self.main_move = 3 #the settlements to place
        self.townstoplay = self.player.towns.copy()
        self.old_action = None

        return True

    def mainmove(self):
        if not self.startmove():
            return False

        while (len(self.townstoplay) > 0 or self.main_move > 0) and self.player.settlements != 0:
            print("\nRule Cards: {:^16}{:^16}{:^16}{:^16}\n".format(*[x.name for x in self.rules.rules]))
            print(self.board)
            if self.main_move > 0:
                print("main: Start main move and place three settlements on {:s} ({:s})".format(self.player.card.name, self.player.card.value))
            if len(self.townstoplay) > 0:
                print("Write one of the following town options: ", [x.name for x in self.townstoplay])
            print("end: End move and next player")
            inp = input("Select a option player {:s}\n".format(str(self.player)))

            if inp == "main":
                while self.main_move != 0 and self.player.settlements != 0:
                    moves = self.board.getpossiblemove(self.player, self.player.card)
                    self.board.print_selection(moves)
                    coord, abort = self.getcoordinates()
                    if abort and self.main_move == 3:
                        break
                    if coord:
                        if self.place_settlement(*coord, self.player.card):
                            self.main_move -= 1                
                continue
            elif inp == "end":
                if self.main_move == 0 or self.player.settlements == 0:
                    break
                else:
                    print("Please place three settlements (mandatory action)")
                continue

            try:
                town_special = BOARDSECTIONS[inp.upper()]
            except:
                print("given town name {:s} unknown".format(inp))
                continue

            if town_special not in self.townstoplay:
                print("player has not this town or is already played this round".format(inp))
                continue

            if town_special == BOARDSECTIONS.FARM:
                while 1:
                    moves = self.board.getpossiblemove(self.player, TERRAIN.GRASS)
                    self.board.print_selection(moves)
                    coord, abort = self.getcoordinates()
                    if abort:
                        break
                    if coord:
                        if self.place_settlement(*coord, TERRAIN.GRASS):
                            self.townstoplay.remove(BOARDSECTIONS.FARM)
                            break
            elif town_special == BOARDSECTIONS.PADDOCK:
                while 1:
                    moves = self.board.getpossiblemove(self.player, str(self.player))
                    self.board.print_selection(moves)
                    print("Select a settlement for moving")
                    coord_from, abort = self.getcoordinates()
                    if abort:
                        break
                    if coord_from and self.board.hassettlement(self.player, *coord_from):
                        moves = self.board.getpossiblepaddockmove(self.player, *coord_from)
                        if len(moves) == 0:
                            print("No moving possbile with this selection")
                            continue
                        self.board.print_selection(moves)
                        print("Jump to...")
                        coord_to, abort = self.getcoordinates()
                        if abort:
                            break
                        if coord_to and coord_to in moves:
                            if self.move_settlement(*coord_from, *coord_to):
                                self.townstoplay.remove(BOARDSECTIONS.PADDOCK)
                                break
            elif town_special == BOARDSECTIONS.ORACLE:
                while 1:
                    moves = self.board.getpossiblemove(self.player, self.player.card)
                    self.board.print_selection(moves)
                    coord, abort = self.getcoordinates()
                    if abort:
                        break
                    if coord:
                        if self.place_settlement(*coord, self.player.card):
                            self.townstoplay.remove(BOARDSECTIONS.ORACLE)
                            break
            elif town_special == BOARDSECTIONS.HARBOR:
                while 1:
                    moves = self.board.getpossiblemove(self.player, str(self.player))
                    self.board.print_selection(moves)
                    print("Select a settlement for moving")
                    coord_from, abort = self.getcoordinates()
                    if abort:
                        break
                    if coord_from and self.board.hassettlement(self.player, *coord_from):
                        moves = self.board.getpossiblemove(self.player, SPECIALLOCATION.WATER, coord_from)
                        if len(moves) == 0:
                            print("No moving possible with this selection")
                            continue
                        self.board.print_selection(moves)
                        print("Go to...")
                        coord_to, abort = self.getcoordinates()
                        if abort:
                            break
                        if coord_to and coord_to in moves:
                            if self.move_settlement(*coord_from, *coord_to):
                                self.townstoplay.remove(BOARDSECTIONS.HARBOR)
                                break
        self.endmove()

        return True

    def endmove(self):
        self.player.takecard()
        self.nextPlayer()