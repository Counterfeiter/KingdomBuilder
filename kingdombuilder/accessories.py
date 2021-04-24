from enum import Enum, unique

@unique
class BOARDSECTIONS(Enum):
    ORACLE = 0
    FARM = 1
    OASIS = 2
    TOWER = 3
    TAVERN = 4
    BARN = 5
    HARBOR = 6
    PADDOCK = 7

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
    MERCHANTS = 10 #TODO add logic to rule engine

    @staticmethod
    def list():
        return list(CARDRULES)