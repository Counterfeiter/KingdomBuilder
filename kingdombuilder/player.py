import random

from .accessories import CARDRULES, TERRAIN, SPECIALLOCATION, BOARDSECTIONS

class Player:
    MAX_SETTLEMENTS = 40
    def __init__(self, index:str, deterministic_cards = False):

        if deterministic_cards:
            #take 100 cards from virtual stack
            self.deterministic_card_stack = random.choices(TERRAIN.list(), k=100)
        else:
            self.deterministic_card_stack = []

        self.takecard()
        self.player_index = index
        self.starter = False # player starts the round
        self.__score = 0
        self.settlements = self.MAX_SETTLEMENTS
        self.towns = []

    @property
    def card(self):
        return self.current_card

    def takecard(self):
        if len(self.deterministic_card_stack) > 0:
            self.current_card = self.deterministic_card_stack.pop(0)
        else:
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
        if self.settlements > self.MAX_SETTLEMENTS:
            raise ValueError()

    def isfinished(self):
        return self.settlements == 0


    @property
    def score(self):
        return self.__score

    @score.setter
    def score(self, score):
        self.__score = score

    def __str__(self):
        return self.player_index

    def __int__(self):
        return int(self.player_index)