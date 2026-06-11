# recovered via pycdc

arenaType = getattr(BigWorld.player(), 'arenaGuiType', None)
if arenaType is not None and arenaType == 400:
    return False
