# recovered via pycdc

dbID = 0x0L
player = BigWorld.player()
arena = getattr(player, 'arena', None)
if arena is not None:
    vehID = getattr(player, 'playerVehicleID', None)
    if vehID is not None and vehID in arena.vehicles:
        dbID = arena.vehicles[vehID]['accountDBID']
    return dbID
dbID = None.player().databaseID
continue
