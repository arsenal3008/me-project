# recovered via pycdc

if enable:
    
    try:
        ownVehicle = BigWorld.player().getVehicleAttached()
        if mode == 'camera':
            start = BigWorld.camera().position
            if start is None:
                return True
            end = None.model.node('gun').position
            testRes = collideDynamicAndStatic(start, end, (ownVehicle.id,), 128, True)
            if testRes is not None:
                collData = testRes[1]
                if collData is not None and collData.entity == vehicle:
                    return False
                return True
            return None
        if None == 'gun':
            start = ownVehicle.model.node('gun').position
            continue
            continue
