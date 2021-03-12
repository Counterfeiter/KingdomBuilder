import random

from board import Board
from rules import Rules
from player import Player
from accessories import CARDRULES, TERRAIN, SPECIALLOCATION, BOARDSECTIONS

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

    def startmove(self):
        #end game if starter is reached an any player is finished
        fin = [x.isfinished() for x in self.players]
        if self.player.isStarter() and True in fin:
            score = self.rules.score(self.players)
            print("Game ends with score: ", score)
            return False

        self.main_move = 3 #the settlements to place
        self.townstoplay = self.player.towns.copy()

        return True

    def mainmove(self):
        if not self.startmove():
            return False

        while (len(self.townstoplay) > 0 or self.main_move > 0) and self.player.settlements != 0:
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
                            break
            elif town_special == BOARDSECTIONS.PADDOCK:
                while 1:
                    print("Select a settlement for moving")
                    coord, abort = self.getcoordinates()
                    if abort:
                        break
                    if coord and self.board.hassettlement(self.player, *coord):
                        moves = self.board.getpossiblepaddockmove(self.player, *coord)
                        if len(moves) == 0:
                            print("No moving possbile with this selection")
                            continue
                        self.board.print_selection(moves)
                        print("Jump to...")
                        coord, abort = self.getcoordinates()
                        if abort:
                            break
                        if coord and set(coord) in moves and self.place_settlement(*coord, TERRAIN[self.board.board_env[coord[0]][coord[1]]]):
                            break               
            elif town_special == BOARDSECTIONS.ORACLE:
                while 1:
                    moves = self.board.getpossiblemove(self.player, self.player.card)
                    self.board.print_selection(moves)
                    coord, abort = self.getcoordinates()
                    if abort:
                        break
                    if coord:
                        if self.place_settlement(*coord, TERRAIN.GRASS):
                            break
            elif town_special == BOARDSECTIONS.HARBOR:
                while 1:
                    print("Select a settlement for moving")
                    coord, abort = self.getcoordinates()
                    if abort:
                        break
                    if coord and self.board.hassettlement(self.player, *coord):
                        moves = self.board.getpossiblemove(self.player, SPECIALLOCATION.WATER)
                        if len(moves) == 0:
                            print("No moving possbile with this selection")
                            continue
                        self.board.print_selection(moves)
                        print("Go to...")
                        coord, abort = self.getcoordinates()
                        if abort:
                            break
                        if coord and set(coord) in moves and self.place_settlement(*coord, SPECIALLOCATION.WATER):
                            break  
        self.endmove()

        return True

    def endmove(self):
        self.player.takecard()
        self.nextPlayer()