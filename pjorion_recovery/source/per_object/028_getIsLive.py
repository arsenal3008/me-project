# recovered via pycdc

try:
    if getBattleOn():
        pass
    return BigWorld.player().arena.vehicles.get(id)['isAlive']
except:
    return None
