from enum import Enum, unique
import random
import configparser
from typing import OrderedDict
import collections

from .board import Board
from .rules import Rules
from .player import Player
from .accessories import CARDRULES, TERRAIN, SPECIALLOCATION, BOARDSECTIONS

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
    TOWER = 12
    TAVERN = 13

class Game:
    def __init__(self, num_players : int, quadrants : list = [], rotations : list = [], rules : list = [], deterministic = False):
        # 4 player is orginal... 
        # but in expansion modes you get settlements for a 5th player
        if num_players < 1 or num_players > 5:
            raise ValueError()
        #init random quadrants from folder quadrants
        self.board = Board(quadrants, rotations)
        #init random rules cards
        self.rules = Rules(self.board, rules)
        #init players
        self.players = [ Player(str(ind), deterministic) for ind in range(1, num_players + 1) ]
        #set random start player
        self.current_player = random.randrange(0, num_players)
        self.players[self.current_player].setStarter()
        self.townstoplay = []
        self.game_done = False
        self.main_move = 3
        self.old_action = DOACTION.END
        self.select_coord = [] # coordinates [row, col] of a selection move (PADDOCK, HARBOR, BARN)
        # use this setting to draw a card from stack before a players move start and not if it ends
        # this setting is usefull for some tree search algo. 
        self.drawcardbefore = False #always false - this setting could be only modified by loading a game

    def gamestate_to_dict(self):
        game_state = {
            'GAME': {
                'current_player' : self.current_player,
                'townstoplay' : self.townstoplay.copy(),#[t.name for t in self.townstoplay],
                'done' : self.game_done,
                'mainmovesettements' : self.main_move,
                'oldaction' : self.old_action,
                'selectedcoord' : self.select_coord[:],
            },
            'PLAYERS' : {
                'num_of': len(self.players),
                'starter': [x.isStarter() for x in self.players].index(True),
                'drawcardbefore': self.drawcardbefore, 
            },
            'RULES' : {
                'rules': self.rules.rules.copy(),#[x.name for x in self.rules.rules]
            },
            'BOARD' : {
                'quadrants': self.board.quadrant_order.copy(),
                'rotation': self.board.board_rotations.copy(),
                'board': [row[:] for row in self.board.board_merged],#'->\n' + str(self.board)
            }
        }

        for player in self.players:
            game_state['PLAYER' + str(player)] = \
            {
                'settlements': player.settlements,
                'towns': player.towns.copy(),#[t.name for t in player.towns],
                'card': player.current_card,
                'stack': player.deterministic_card_stack.copy(),#[x.name for x in player.deterministic_card_stack]
            }

        return game_state

    def dict_to_gamestate(self, game_state : dict):
        self.current_player = game_state['GAME']['current_player']
        self.townstoplay = game_state['GAME']['townstoplay'] #[BOARDSECTIONS[x.upper()] for x in game_state['GAME']['townstoplay'].split(',').replace(' ','')]
        self.game_done = game_state['GAME']['done']
        self.main_move = game_state['GAME']['mainmovesettements']
        self.old_action = game_state['GAME']['oldaction']
        self.select_coord = game_state['GAME']['selectedcoord']

        self.drawcardbefore = game_state['PLAYERS']['drawcardbefore']
        self.players = []
        for i in range(game_state['PLAYERS']['num_of']):
            player_str = str(i+1)
            self.players.append(Player(player_str))
            self.players[-1].starter = True if game_state['PLAYERS']['starter']==i else False
            self.players[-1].settlements = game_state['PLAYER' + player_str]['settlements']
            self.players[-1].towns = game_state['PLAYER' + player_str]['towns']
            self.players[-1].current_card = game_state['PLAYER' + player_str]['card']
            self.players[-1].deterministic_card_stack = game_state['PLAYER' + player_str]['stack']
        self.rules.rules = game_state['RULES']['rules']
        self.board = Board(game_state['BOARD']['quadrants'], game_state['BOARD']['rotation'])
        self.rules.board = self.board

        towns = [SPECIALLOCATION.TOWNEMPTY.value, SPECIALLOCATION.TOWNFULL.value, SPECIALLOCATION.TOWNHALF.value]
        player_list = [str(x) for x in self.players]
        for row in range(20):
            for col in range(20):
                if game_state['BOARD']['board'][row][col] in player_list:
                    self.board.board_settlements[row][col] = game_state['BOARD']['board'][row][col]
                if game_state['BOARD']['board'][row][col] in towns:
                    self.board.board_env[row][col] = game_state['BOARD']['board'][row][col]

        self.board.resulting_board(force_refresh=True)
        #[row.split() for row in game_state['BOARD']['board'].strip().split("\n")]

    # store it in a format that could be read and modified by humans
    def save(self, filename : str):
        parser = configparser.ConfigParser()
        game_dict = self.gamestate_to_dict()

        #better indexing for humans
        game_dict['PLAYERS']['starter'] += 1
        game_dict['GAME']['current_player'] += 1

        parser.read_dict(game_dict)
        parser.remove_option('BOARD', 'board')

        parser["GAME"]["townstoplay"] = ",".join([x.name for x in game_dict["GAME"]["townstoplay"]])
        parser['GAME']['oldaction'] = game_dict['GAME']['oldaction'].name
        parser['GAME']['selectedcoord'] = ",".join([str(x) for x in game_dict['GAME']['selectedcoord']])
        parser['RULES']['rules'] = ",".join([x.name for x in game_dict['RULES']['rules']])
        parser['BOARD']['quadrants'] = ",".join(game_dict['BOARD']['quadrants'])
        parser['BOARD']['rotation'] = ",".join([str(x) for x in game_dict['BOARD']['rotation']])

        for i, row in enumerate(game_dict['BOARD']['board']):
            if i % 2:
                key = "{:03d}".format(i)
            else:
                key = "{:02d}".format(i)

            parser['BOARD'][key] = ",".join(row)

        for i in range(game_dict['PLAYERS']['num_of']):
            player_str = str(i+1)
            parser['PLAYER' + player_str]['towns'] = ",".join([x.name for x in game_dict['PLAYER' + player_str]['towns']])
            parser['PLAYER' + player_str]['card'] = game_dict['PLAYER' + player_str]['card'].name
            parser['PLAYER' + player_str]['stack'] = ",".join([x.name for x in game_dict['PLAYER' + player_str]['stack']])
            

        try:
            with open(filename, 'w') as configfile:
                parser.write(configfile)
        except Exception as e:
            print("Error while saving game to file!")
            print(str(e))

    @staticmethod
    def load(filename : str):
        parser = configparser.ConfigParser()
        try:
            parser.read(filename)
        except Exception as e:
            print("Error while loading saved game!")
            print(str(e))
        else:
            # a kind of hack... TODO: make it clean
            game_config = {s:dict(parser.items(s)) for s in parser.sections()}
            game_config['GAME']['current_player'] = int(game_config['GAME']['current_player']) - 1
            game_config['GAME']['townstoplay'] = [BOARDSECTIONS[name.upper()] for name in filter(None, game_config['GAME']['townstoplay'].replace(' ', '').split(','))]
            game_config['GAME']['done'] = game_config['GAME']['done'].lower() == 'true'
            game_config['GAME']['mainmovesettements'] = int(game_config['GAME']['mainmovesettements'])
            game_config['GAME']['oldaction'] = DOACTION[game_config['GAME']['oldaction'].upper()]
            game_config['GAME']['selectedcoord'] = [int(x) for x in filter(None, game_config['GAME']['selectedcoord'].replace(' ', '').split(','))]

            game_config['RULES']['rules'] = [CARDRULES[name.upper()] for name in game_config['RULES']['rules'].replace(' ', '').split(',')]

            game_config['BOARD']['quadrants'] = [x for x in game_config['BOARD']['quadrants'].replace(' ', '').split(',')]
            game_config['BOARD']['rotation'] = [x.lower() == 'true' for x in game_config['BOARD']['rotation'].replace(' ', '').split(',')]

            game_config['PLAYERS']['num_of'] = int(game_config['PLAYERS']['num_of'])
            game_config['PLAYERS']['starter'] = int(game_config['PLAYERS']['starter']) - 1
            game_config['PLAYERS']['drawcardbefore'] = game_config['PLAYERS']['drawcardbefore'].lower() == 'true'

            game_config['BOARD']['board'] = [[]]*20
            for i in range(20):
                if i % 2:
                    key = "{:03d}".format(i)
                else:
                    key = "{:02d}".format(i)

                game_config['BOARD']['board'][i] = [x for x in game_config['BOARD'][key].replace(' ', '').split(',')]

            for i in range(game_config['PLAYERS']['num_of']):
                player_str = str(i+1)
                game_config['PLAYER' + player_str]['towns'] = [BOARDSECTIONS[name.upper()] for name in filter(None, game_config['PLAYER' + player_str]['towns'].replace(' ', '').split(','))]
                game_config['PLAYER' + player_str]['card'] = TERRAIN[game_config['PLAYER' + player_str]['card'].upper()]
                game_config['PLAYER' + player_str]['stack'] = [TERRAIN[name.upper()] for name in filter(None, game_config['PLAYER' + player_str]['stack'].replace(' ', '').split(','))]
                game_config['PLAYER' + player_str]['settlements'] = int(game_config['PLAYER' + player_str]['settlements'])

            game = Game(game_config['PLAYERS']['num_of'])
            game.dict_to_gamestate(game_config)
        
        return game


    @property
    def player(self):
        return self.players[self.current_player]

    def nextPlayer(self):
        self.current_player += 1
        if self.current_player >= len(self.players):
            self.current_player = 0

    def place_settlement(self, row, col, env_rule = None):
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

    def getcoordinates(self, action = "-"):
        inp = input("Player {:s} enter row, col or type abort ({})\n".format(str(self.player), action))
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
        return self.old_action == pass_if or self.old_action not in [DOACTION.HARBORSELECT,
                                                    DOACTION.PADDOCKSELECT, DOACTION.HARBORSELECT, DOACTION.BARNSELECT]

    def actionstomoves(self):
        # pa = possible actions
        pa = OrderedDict()
        
        pa[DOACTION.TAKENEWCARD] = [[0]]
        pa[DOACTION.END] = [[1]] if self.main_move == 0 or self.player.settlements == 0 else [[0]]
        ### could be done in a loop... but it is a ordered dict, we will leave at as reference
        # for the flattend action mask array
        pa[DOACTION.MAINMOVE] = [ [0]*20 for _ in range(20)]
        pa[DOACTION.ORACLE] = [ [0]*20 for _ in range(20)]
        pa[DOACTION.FARM] = [ [0]*20 for _ in range(20)]
        pa[DOACTION.HARBORSELECT] = [ [0]*20 for _ in range(20)]
        pa[DOACTION.HARBORSET] = [ [0]*20 for _ in range(20)]
        pa[DOACTION.PADDOCKSELECT] = [ [0]*20 for _ in range(20)]
        pa[DOACTION.PADDOCKSET] = [ [0]*20 for _ in range(20)]
        ##additional 4 board quadrants
        pa[DOACTION.OASIS] = [ [0]*20 for _ in range(20)]
        pa[DOACTION.BARNSELECT] = [ [0]*20 for _ in range(20)]
        pa[DOACTION.BARNSET] = [ [0]*20 for _ in range(20)]
        pa[DOACTION.TOWER] = [ [0]*20 for _ in range(20)]
        pa[DOACTION.TAVERN] = [ [0]*20 for _ in range(20)]
        

        if self.main_move > 0 and self.player.settlements > 0:
            moves = self.board.getpossiblemove(self.player, self.player.card)
            for coord in moves:
                pa[DOACTION.MAINMOVE][coord[0]][coord[1]] = 1
            #check if player could take a new card 
            if len(moves) <= 0:
                pa[DOACTION.TAKENEWCARD][0][0] = 1

        if self.checktownplay_possible(BOARDSECTIONS.FARM):
            moves = self.board.getpossiblemove(self.player, TERRAIN.GRASS)
            for coord in moves:
                pa[DOACTION.FARM][coord[0]][coord[1]] = 1

        if self.checktownplay_possible(BOARDSECTIONS.ORACLE):
            moves = self.board.getpossiblemove(self.player, self.player.card)
            for coord in moves:
                pa[DOACTION.ORACLE][coord[0]][coord[1]] = 1
            if len(moves) <= 0:
                pa[DOACTION.TAKENEWCARD][0][0] = 1

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
                moves = self.board.getpossiblemove(self.player, self.player.card, self.select_coord)
                for coord in moves:
                    pa[DOACTION.BARNSET][coord[0]][coord[1]] = 1
                if len(moves) <= 0:
                    pa[DOACTION.TAKENEWCARD][0] = 1

        if self.checktownplay_possible(BOARDSECTIONS.TOWER):
            moves = self.board.getpossibletowermove(self.player)
            for coord in moves:
                pa[DOACTION.TOWER][coord[0]][coord[1]] = 1

        if self.checktownplay_possible(BOARDSECTIONS.TAVERN):
            moves = self.board.getpossibletavernmove(self.player)
            for coord in moves:
                pa[DOACTION.TAVERN][coord[0]][coord[1]] = 1

        return pa

    #controlled by an rl agent?
    def singlestepmove(self, action : DOACTION, row, col):
        res = self._singlestepmove(action, row, col)
        if res:
            #store old action if move was valid
            self.old_action = action
        else:
            print("Invalid move selected: ", action, row, col, " for player ", self.player, " with card ", self.player.card)
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
        elif action == DOACTION.OASIS and BOARDSECTIONS.OASIS in self.townstoplay:
            if self.place_settlement(row, col, TERRAIN.DESERT):
                self.townstoplay.remove(BOARDSECTIONS.OASIS)
                return True
        elif action == DOACTION.BARNSELECT and BOARDSECTIONS.BARN in self.townstoplay:
            if self.board.hassettlement(self.player, row, col):
                self.select_coord = (row, col)
                return True
        elif action == DOACTION.BARNSET and self.old_action == DOACTION.BARNSELECT:
            moves = self.board.getpossiblemove(self.player, self.player.card, self.select_coord)
            if (row, col) not in moves:
                return False
            if self.board.move_settlement(self.player, *self.select_coord, row, col):
                self.townstoplay.remove(BOARDSECTIONS.BARN)
                return True
        elif action == DOACTION.TOWER and BOARDSECTIONS.TOWER in self.townstoplay:
            moves = self.board.getpossibletowermove(self.player)
            if (row, col) not in moves:
                return False
            if self.place_settlement(row, col):
                self.townstoplay.remove(BOARDSECTIONS.TOWER)
                return True
        elif action == DOACTION.TAVERN and BOARDSECTIONS.TAVERN in self.townstoplay:
            moves = self.board.getpossibletavernmove(self.player)
            if (row, col) not in moves:
                return False
            if self.place_settlement(row, col):
                self.townstoplay.remove(BOARDSECTIONS.TAVERN)
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

    def score(self):
        #also score is saved to player class
        return self.rules.score(self.players)
            
    def startmove(self):
        if self.drawcardbefore:
            self.player.takecard()
        #end game if starter is reached an any player is finished
        fin = [x.isfinished() for x in self.players]
        if self.player.isStarter() and True in fin:
            score = self.score()
            #print("Game ends with score: ", score)
            self.game_done = True
            return False

        self.main_move = 3 #the settlements to place
        self.townstoplay = self.player.towns.copy()
        self.old_action = None

        return True

    def consoleplayermove(self):
        current_player = self.player
        while current_player == self.player:
            print(self)
            possbile_action_dict = self.actionstomoves()
            pos_actions_enums = []
            for action, moves in possbile_action_dict.items():
                if max(map(max, moves)) >= 1:
                    pos_actions_enums.append(action)
            if len(pos_actions_enums) == 1:
                action_selected = pos_actions_enums[0]
            else:
                print("Player ", str(self.player), " has options to play: ", [x.name for x in pos_actions_enums])
                inp = input("Select a option player {:s}\n".format(str(self.player)))
                try:
                    action_selected = DOACTION[inp.upper()]
                    if action_selected not in pos_actions_enums:
                        print("Given action {} is not possible in this situation".format(inp))
                        continue
                except:
                    print("Given action {} unknown".format(inp))
                    continue

            if action_selected == DOACTION.END or action_selected == DOACTION.TAKENEWCARD:
                assert self.singlestepmove(action_selected, 0, 0) == True
                continue

            print("\nRule Cards: {:^16}{:^16}{:^16}{:^16}\n".format(*[x.name for x in self.rules.rules]))
            self.board.print_selection(possbile_action_dict[action_selected])
            coord, abort = self.getcoordinates(action_selected.name)
            if abort:
                continue
            if coord:
                if self.singlestepmove(action_selected, *coord):
                    continue
            print("Coordinates not valid")            

        return not self.done

    def endmove(self):
        if self.drawcardbefore == False:
            self.player.takecard()
        self.nextPlayer()

    def __str__(self):
        return "\nRule Cards: {:^16}{:^16}{:^16}{:^16}\n".format(*[x.name for x in self.rules.rules]) + str(self.board)


if __name__ == "__main__":
    ### start a random two player game (selfplay)
    game = Game(2)

    try:
        while game.consoleplayermove():
            pass
    except KeyboardInterrupt:
        print("Abort game...")
    else:
        print("### Game done! ###")
        for player in game.players:
            print("Player {:s} score: {:d}".format(player, player.score))