# recovered via pycdc

if mody.modEnable and isinstance(entity, Vehicle) and entity.isAlive():
    for vehicle in BigWorld.entities.values():
        if isinstance(vehicle, Vehicle) or BigWorld.target() == vehicle:
            vehicle.zj_adgclr = None
        removeEdge(vehicle)
    
old_targetFocus(self, entity)
