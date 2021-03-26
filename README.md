# Kingdom Builder Console Board Game

Python implementation of the Kingdom Builder rules and game play

## Getting Started

This little python scripts could be used to play a kindom builder game with the command line interface.
Because this is a pain, it would be great to have a browser based (js) frontend.

Rules: https://ssl.queen-games.com/dl/rules/kingdom-builder_en.pdf

### Why?

This is the first step to start an AI challenge.
gym wrapper is follwing in the upcomming commits.

### Preview

```
Player 2 with Terrain CANYON and towns to play:  [BOARDSECTIONS.FARM: 2]

Rule Cards:      CASTLE          MINERS        FISHERMEN         WORKER     

                 ORACLE                                 PADDOCK                 
      00  01  02  03  04  05  06  07  08  09  10  11  12  13  14  15  16  17  18  19 
00   G   G   G   F   F   W   G   F   F   F   S   2   2   2   2   W   D   D   D   D     00
01     G   G   G   C   F   W   G   F   F   F   M   M   2   2   2   W   D   D   D   D   01
02   G   B   2   G   F   F   W   G   G   F   M   M   S   M   M   W   D   D   T   B     02
03     B   B   2   G   F   W   B   T   F   F   M   S   M   M   W   M   D   B   B   B   03
04   B   B   B   2   S   W   B   B   W   W   S   1   F   F   W   M   M   S   B   B     04
05     M   M   2   G   G   W   W   W   D   1   1   F   F   W   S   S   S   M   B   B   05
06   S   S   2   M   G   2   2   2   1   1   1   t   F   F   W   B   B   B   B   B     06
07     S   S   C   2   M   1   2   2   1   1   1   G   F   W   G   C   G   B   G   F   07
08   W   W   W   2   2   1   2   M   2   1   G   G   F   F   W   G   G   G   G   F     08
09     W   W   W   W   2   1   1   1   1   S   G   G   F   F   W   G   G   G   F   F   09
10   G   G   F   F   F   W   1   F   F   1   D   D   S   W   W   F   F   F   G   G     10
11     G   B   F   F   W   1   F   F   1   1   D   C   S   W   F   F   F   T   G   G   11
12   G   B   B   F   W   G   G   1   1   1   S   S   S   B   B   B   F   S   B   B     12
13     B   B   F   F   W   G   M   B   D   D   S   S   B   B   W   D   D   S   S   B   13
14   S   B   C   F   W   G   D   D   D   D   S   G   G   W   B   B   D   D   S   S     14
15     S   S   F   W   G   G   M   M   D   D   G   2   t   B   W   B   W   D   D   S   15
16   S   S   W   W   W   G   D   D   D   S   2   2   2   F   B   B   W   W   D   D     16
17     W   W   G   G   W   W   T   S   M   S   G   G   F   F   M   W   W   W   D   W   17
18   W   D   C   G   W   M   W   S   S   S   G   M   F   F   W   W   W   W   W   W     18
19     W   D   D   W   W   W   W   S   S   S   F   F   F   W   W   W   W   W   W   W   19
      00  01  02  03  04  05  06  07  08  09  10  11  12  13  14  15  16  17  18  19 
                 HARBOR                                   FARM                  
```

### Play It Online (third party)

Playing against bots:
https://ssl.queen-games.com/die-kingdom-builder-web-app/

Play with your friends:
https://boardgamearena.com/

### Prerequisites

Pure python 3

#### Execution speed

If you train an AI engine the game engine is maybe the bottleneck. 
Because of the pure python concept, there is no speed improve with numpy. Maybe I will drop this concept later.

Speed could be improved:
1. rework the code and stay pure python
2. switch to numpy
3. track only changes (place, move settlement) and stop rebuilding the lists

### Installing

Clone and play around

## Authors

* **Sebastian Förster** - *Initial work*

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* this post gives me the start impulse and a tip for grid interfacing: https://codegolf.stackexchange.com/questions/44485/score-a-game-of-kingdom-builder