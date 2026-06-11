# recovered via pycdc

if not mody.modEnable:
    for vehicle in BigWorld.entities.values():
        if isinstance(vehicle, Vehicle) and vehicle.isStarted:
            removeEdge(vehicle)
    return None
if (None.target() is None or isinstance(BigWorld.target(), Vehicle)) and not BigWorld.target().isAlive():
    fam = 0
    for vehicle in BigWorld.entities.values():
        if isinstance(vehicle, Vehicle) and vehicle.isStarted:
            adgclr = None
            t_clr = getattr(vehicle, 'zj_adgclr', None)
            if mody.freeAttackMarker and vehicle.publicInfo['team'] != BigWorld.player().team and not GetObstacle(vehicle, 'gun', mody.freeAttackMarker) and GetVehicleViewAngle(vehicle, 0.7):
                adgclr = vehicle.zj_adgclr = 3
                if t_clr != adgclr:
                    addEdge(vehicle)
                    continue
                    if fam == 3:
                        removeEdge(vehicle)
                        continue
        distance = (BigWorld.player().getOwnVehiclePosition() - vehicle.position).length
        if vehicle.isAlive() and vehicle.publicInfo['team'] != BigWorld.player().team and not (vehicle.isPlayerVehicle) or distance < distance:
            if distance < mody.distanceFar and GetObstacle(vehicle, 'camera', mody.forObstacleOnlyEnemies) and GetVehicleViewAngle(vehicle, mody.viewAngle, mody.viewAngleEnable):
                if BigWorld.player().inputHandler.ctrlModeName not in ('sniper', 'dualgun', 'twinGun'):
                    pass
                if not (mody.sniperOnly) or mody.altFlag:
                    vehicle.zj_adgclr = 0
                    if adgclr != 3:
                        adgclr = vehicle.zj_adgclr
                    if t_clr != adgclr:
                        addEdge(vehicle)
                        continue
                        removeEdge(vehicle)
                        continue
                    if mody.batleStart and mody.modEnable:
                        BigWorld.callback(mody.tick, DrawControl)
