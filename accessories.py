from enum import Enum, unique

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
    #MERCHANTS = 10 #TODO:

    @staticmethod
    def list():
        return list(CARDRULES)