# recovered via pycdc

methodcaller = methodcaller
import operator
PlayerMessages = PlayerMessages
import gui.Scaleform.daapi.view.battle.shared.messages.player_messages
old_PlayerMessages_init = PlayerMessages.__init__

def new_PlayerMessages_init(self):
    old_PlayerMessages_init(self)
    PlayerAvatar.selfMsg = self

PlayerMessages.__init__ = new_PlayerMessages_init

def addEdge(vehicle):
    if mody.modEnable and isinstance(vehicle, Vehicle) and vehicle.isStarted and vehicle.isAlive():
        removeEdge(vehicle, False)
        vehicle.drawEdge()


def removeEdge(vehicle, force = (True,)):
    if isinstance(vehicle, Vehicle) and vehicle.isStarted:
        if (not vehicle.isAlive() or BigWorld.target() != vehicle) and force:
            vehicle.zj_adgclr = None
        vehicle.removeEdge()


def DrawControl():
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


def onVehicleKilled(targetID, *args):
    vehicle = BigWorld.entity(targetID)
    removeEdge(vehicle)


def new_startVisual(self, old_func = Vehicle.startVisual):
    old_func(self)


def new_stopVisual(self, vehicle, old_func = (PlayerAvatar.vehicle_onLeaveWorld,)):
    removeEdge(vehicle)
    old_func(self, vehicle)

Vehicle.startVisual = new_startVisual
PlayerAvatar.vehicle_onLeaveWorld = new_stopVisual

def new_targetFocus(self, entity, old_targetFocus = (None, ((None, None, None, None, None, None, (None, None, (None, None))),), PlayerAvatar.targetFocus)):
    if mody.modEnable and isinstance(entity, Vehicle) and entity.isAlive():
        for vehicle in BigWorld.entities.values():
            if isinstance(vehicle, Vehicle) or BigWorld.target() == vehicle:
                vehicle.zj_adgclr = None
            removeEdge(vehicle)
        
    old_targetFocus(self, entity)


def new_targetBlur(self, prevEntity, old_targetBlur = (None, PlayerAvatar.targetBlur)):
    old_targetBlur(self, prevEntity)
    if mody.modEnable:
        for vehicle in BigWorld.entities.values():
            if isinstance(vehicle, Vehicle):
                pass

PlayerAvatar.targetFocus = new_targetFocus
PlayerAvatar.targetBlur = new_targetBlur
if IS_LESTA:
    
    def new_doHighlightOperation(self, status, args):
        if (not (mody.modEnable) or BigWorld.target()) and BigWorld.target().isAlive():
            old_doHighlightOperation(self, status, args)
            return None
        vehicle = None._Highlighter__vehicle
        if status & self.HIGHLIGHT_ON:
            adgclr = getattr(vehicle, 'zj_adgclr', None)
            if adgclr is not None:
                args = (adgclr, False, 0, False)
            BigWorld.addEdgeDetectEntity(vehicle, self._Highlighter__collisions, *args)
            self._Highlighter__updateHighlightComponent(status, args)
            return None
        None.delEdgeDetectEntity(vehicle)
        continue

    old_doHighlightOperation = Highlighter._Highlighter__doHighlightOperation
    Highlighter._Highlighter__doHighlightOperation = new_doHighlightOperation
    
    def GetVehicleViewAngle(vehicle, viewAngle, enable = (True,)):
