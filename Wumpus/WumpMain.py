

from players import UserPlayer
from naiveBayesPlayer import NaiveBayesPlayer
from wumpWorld import WumpWorld


def wumpusGame(MakePlayer):
    rows = 8
    cols = 8
    world = WumpWorld(rows, cols)
    world.wumpMap.printGrid()
    pr, pc = world.getHeroLoc()
    userP = MakePlayer((pr, pc), (rows, cols))
    while True:
        senses = world.heroSenses()
        act = userP.nextAction(senses)
        if act == 'q':
            break
        else:
            if act[0] == 'move':  # moving
                result, newLoc = world.moveHero(act[1])
            else:
                result = world.shootArrow(act[1])

            if not world.isWumpusAlive():
                print("You killed the Wumpus!")
                print("CONGRATULATIONS!")
                break
            elif not world.isHeroAlive():
                print("Result =", result)
                if result == 'pit':
                    print("You fell in a pit and died!")
                    break
                elif result == 'wumpus':
                    print("You met the Wumpus! It ate you.")
                    break
                else:
                    print("wumpusGame: should never get here, player dead and no cause.")
            else:
                userP.playerMoved(result, newLoc)
    print("Game over...")



if __name__ == "__main__":
    # wumpusGame(UserPlayer)
    wumpusGame(NaiveBayesPlayer)
