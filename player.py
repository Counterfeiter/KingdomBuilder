import random

from accessories import CARDRULES, TERRAIN, SPECIALLOCATION, BOARDSECTIONS

class Player:
    def __init__(self, index:str):
        self.takecard()
        self.player_index = index
        self.starter = False # player starts the round
        self._score = 0
        self.settlements = 40
        self.towns = []

    @property
    def card(self):
        return self.current_card

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