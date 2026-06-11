# recovered via pycdc

if mody.modEnable and isinstance(vehicle, Vehicle) and vehicle.isStarted and vehicle.isAlive():
    removeEdge(vehicle, False)
    vehicle.drawEdge()
