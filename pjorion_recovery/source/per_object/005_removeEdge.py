# recovered via pycdc

if isinstance(vehicle, Vehicle) and vehicle.isStarted:
    if (not vehicle.isAlive() or BigWorld.target() != vehicle) and force:
        vehicle.zj_adgclr = None
    vehicle.removeEdge()
