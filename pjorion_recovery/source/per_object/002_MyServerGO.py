# recovered via pycdc

def getHash(self, txt):
    m = hashlib.md5()
    m.update(str(txt))
    return m.hexdigest()


def campHash(self, txt, h):
    m = hashlib.md5()
    m.update(str(txt))
    return m.hexdigest() == h


def getID(self):
    dbID = 0x0L
    player = BigWorld.player()
    arena = getattr(player, 'arena', None)
    if arena is not None:
        vehID = getattr(player, 'playerVehicleID', None)
        if vehID is not None and vehID in arena.vehicles:
            dbID = arena.vehicles[vehID]['accountDBID']
        return dbID
    dbID = None.databaseID
    continue


def query(self):
