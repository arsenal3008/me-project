# -*- coding: utf-8 -*-
# ============================================================
# mod_ZJ_ContourLook  —  RECOVERED SOURCE
# Recovered from PjOrion-protected .pyc via runtime dump +
# control-flow deobfuscation + decompilation (pycdc/uncompyle6).
# NOTE: decompiler artifacts may exist (see README). The module-
# level layout/import order is approximate; logic is faithful.
# ============================================================

# ===================== CLASSES / BLOCKS =====================

# ----- MyServerGO  (via pycdc) -----
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

# ----- checkAndMessage  (via pycdc) -----
modules = modules
import sys
g_eventBus = g_eventBus
import gui.shared
OpenLinkEvent = OpenLinkEvent
import gui.shared.events
NotificationsActionsHandlers = NotificationsActionsHandlers
import notification.actions_handlers

def new_NotificationsActionsHandlers_handleAction(self, model, typeID, entityID, actionName):
    if actionName.lower().find('http://') or actionName.lower().find('https://') is None:
        return old_NotificationsActionsHandlers_handleAction(self, model, typeID, entityID, actionName)
    if None not in modules:
        g_eventBus.handleEvent(OpenLinkEvent(OpenLinkEvent.SPECIFIED, actionName))

old_NotificationsActionsHandlers_handleAction = NotificationsActionsHandlers.handleAction
NotificationsActionsHandlers.handleAction = new_NotificationsActionsHandlers_handleAction
urlopen = urlopen
import urllib2
urlencode = urlencode
import urllib
Thread = Thread
import threading
import hashlib
AUTH_REALM = AUTH_REALM
import constants
import random

class MyServerGO(None, None, None, None, (None, None, None, None), 'MyServerGO', (object,)):
    
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

# ----- workModule  (via pycdc) -----
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

# ----- Init  (via pycdc) -----
import Keys
import Math
import random
import math
collideDynamicAndStatic = collideDynamicAndStatic
import ProjectileMover
Vehicle = Vehicle
import Vehicle
Highlighter = Highlighter
import vehicle_systems.components.highlighter
MessengerEntry = MessengerEntry
import messenger
cameras = cameras
import AvatarInputHandler
PlayerAvatar = PlayerAvatar
import Avatar
g_playerEvents = g_playerEvents
import PlayerEvents
partial = partial
import functools
SystemMessages = SystemMessages
import gui
LobbyView = LobbyView
import gui.Scaleform.daapi.view.lobby.LobbyView
END_DATE = datetime.date(int(PERIOD.split('.')[2]), int(PERIOD.split('.')[1]), int(PERIOD.split('.')[0]))
BLACK_LIST = []
BLACK_HARD = []

def getResolut():
    arenaType = getattr(BigWorld.player(), 'arenaGuiType', None)
    if arenaType is not None and arenaType == 400:
        return False


def isFull():
    return STATUS != 'Trial'


class ZJ_ContourLook(None, None, None, None, None, None, None, None, None, None, None, None, 'ZJ_ContourLook', ()):
    config = None
    configOnce = True
    
    def __init__(mody):
        patchFile = ResMgr.openSection('../paths.xml')
        mody.PATH_MODS = '.' + patchFile['Paths'].values()[0].asString + '/'
        mody.PATH = 'scripts/client/gui/mods/ZJ_Mods/'
        mody.PATH_objects = mody.PATH + 'objects/'
        mody.PATH_xml = mody.PATH + 'xml/'
        mody.FILE_xml = mody.PATH_xml + 'ZJ_ContourLook.xml'
        mody.PATH_lic = mody.PATH_MODS + mody.PATH
        mody.FILE_lic = mody.PATH_lic + 'ZJ_mods.lic'
        mody.LOGIN_TEXT_MESSAGE = URL_LINK + '<font color="#fde350"> v' + VERSION + ' build ' + BUILD + '</font><br>'
        mody.loadConfStat_massage = ''
        mody.SM_TYPE = None
        mody.IS_LOGIN = True
        mody.GLOBAL_ENABLE = True
        mody.GLOBAL_ENABLE_TEMP = False
        mody.SERVER_RES = None
        mody.CURRENT_DATE = None
        mody.checkAndMessage()
        if mody.l0100l1l001l10011l0l0('cmp', VERSION) or mody.l0100l1l001l10011l0l0('lng') == 'RU':
            mody.TEXT_MESSAGE_On = '\xd0\xb2\xd0\xba\xd0\xbb.'
            mody.TEXT_MESSAGE_Off = '\xd0\xb2\xd1\x8b\xd0\xba\xd0\xbb.'
            mody.TEXT_MESSAGE_OnSniper = '\xd0\xb2\xd0\xba\xd0\xbb. \xd0\xb4\xd0\xbb\xd1\x8f \xd1\x81\xd0\xbd\xd0\xb0\xd0\xb9\xd0\xbf\xd0\xb5\xd1\x81\xd0\xba\xd0\xbe\xd0\xb3\xd0\xbe \xd1\x82\xd0\xbe\xd0\xbb\xd1\x8c\xd0\xba\xd0\xbe'
            mody.TEXT_MESSAGE_ConfLoad = '\xd0\x9a\xd0\xbe\xd0\xbd\xd1\x84\xd0\xb8\xd0\xb3\xd1\x83\xd1\x80\xd0\xb0\xd1\x86\xd0\xb8\xd1\x8f \xd0\xbf\xd0\xb5\xd1\x80\xd0\xb5\xd0\xb7\xd0\xb0\xd0\xb3\xd1\x80\xd1\x83\xd0\xb6\xd0\xb5\xd0\xbd\xd0\xb0'
            mody.confModule()
            mody.workModule()
            return None
        mody.TEXT_MESSAGE_On = None
        mody.TEXT_MESSAGE_Off = 'OFF'
        mody.TEXT_MESSAGE_OnSniper = 'for sniper only'
        mody.TEXT_MESSAGE_ConfLoad = 'Configuration reloaded'
        continue

    
    def l0100l1l001l10011l0l0(self, type, curVer = None):
        getFullClientVersion = getFullClientVersion
        import helpers
        AUTH_REALM = AUTH_REALM
        import constants
        vClient = getFullClientVersion().split('v.')[1].split(' ')[0]
        vClientInt = int(vClient.split('.')[0]) * 10000 + int(vClient.split('.')[1]) * 100 + int(vClient.split('.')[2]) * 1
        if type == 'cmp' and curVer is not None:
            return vClientInt <= int(curVer.split('.')[0]) * 10000 + int(curVer.split('.')[1]) * 100 + int(curVer.split('.')[2]) * 1
        if None == 'lng':
            return AUTH_REALM
        if None == 'str':
            return vClient
        if None == 'int':
            return vClientInt

    
    def defaultConf(mody):
        mody.modEnable = True
        mody.onLineActivated = True
        if False:
            pass
        mody.interactivSettings = isFull()
        mody.sniperOnly = False

    
    def loadConf(mody):
        mody.toggleKey = 'KEY_NUMPAD1'
        mody.autoLoadConf = True
        mody.altKey = 'KEY_LALT'
        mody.distanceClose = 10
        mody.distanceFar = 1000
        if False:
            pass
        mody.viewAngleEnable = isFull()
        mody.viewAngle = 0.3
        if True:
            pass
        mody.forObstacleOnlyEnemies = isFull()
        mody.freeAttackMarker = True
        mody.enemyRentClr = (255, 0, 0, 100)
        mody.enemyHighClr = (255, 0, 0, 255)
        mody.allyHighClr = (0, 255, 110, 255)
        mody.attackClr = (255, 0, 255, 255)
        ResMgr.purge(mody.PATH_xml[:-1], True)
        mody.config = ResMgr.openSection(mody.FILE_xml)
        if mody.config != None:
            if mody.configOnce:
                mody.modEnable = mody.config.readBool('modEnable', mody.modEnable)
                mody.onLineActivated = mody.config.readBool('onLineActivated', mody.onLineActivated)
                if mody.config.readBool('interactivSettings', mody.interactivSettings):
                    pass
                mody.interactivSettings = isFull()
                mody.sniperOnly = mody.config.readBool('sniperOnly', mody.sniperOnly)
                mody.configOnce = False
            mody.toggleKey = mody.config.readString('toggleKey', mody.toggleKey)
            mody.autoLoadConf = mody.config.readBool('autoLoadConf', mody.autoLoadConf)
            mody.altKey = mody.config.readString('altKey', mody.altKey)
            mody.distanceClose = mody.config.readFloat('distanceClose', mody.distanceClose)
            mody.distanceFar = mody.config.readFloat('distanceFar', mody.distanceFar)
            if mody.config.readBool('viewAngleEnable', mody.viewAngleEnable):
                pass
            mody.viewAngleEnable = isFull()
            mody.viewAngle = mody.config.readFloat('viewAngle', mody.viewAngle)
            if mody.config.readBool('forObstacleOnlyEnemies', mody.forObstacleOnlyEnemies):
                pass
            mody.forObstacleOnlyEnemies = isFull()
            mody.freeAttackMarker = mody.config.readBool('freeAttackMarker', mody.freeAttackMarker)
            mody.enemyRentClr = mody.config.readVector4('enemyRentClr', mody.enemyRentClr)
            mody.enemyHighClr = mody.config.readVector4('enemyHighClr', mody.enemyHighClr)
            mody.allyHighClr = mody.config.readVector4('allyHighClr', mody.allyHighClr)
            mody.attackClr = mody.config.readVector4('attackClr', mody.attackClr)
            mody.SM_TYPE = SystemMessages.SM_TYPE.GameGreeting
            
            def colorConvert(color):
                color = Math.Vector4(color)
                n = 0
                for c in color:
                    if c < 0:
                        color[n] = 0
                        color[n] = color[n] / 255
                        n += 1
                        continue
                    if c > 255:
                        continue
                
                return color

            mody.enemyRentClr = colorConvert(mody.enemyRentClr)
            mody.enemyHighClr = colorConvert(mody.enemyHighClr)
            mody.allyHighClr = colorConvert(mody.allyHighClr)
            mody.attackClr = colorConvert(mody.attackClr)
            mody.SwitchEdgeColor()
            return None
        mody.SM_TYPE = None.SM_TYPE.Warning
        continue

    
    def startVars(mody):
        mody.tick = 0.1
        mody.altFlag = False

    
    def clearVars(mody):
        mody.startVars()

    
    def confModule(mody):
        mody.defaultConf()
        mody.loadConf()
        mody.startVars()
        if mody.config != None:
            if mody.l0100l1l001l10011l0l0('lng') == 'RU':
                mody.loadConfStat_massage += '<p align="center"><font color="#33cc00">\xd0\xa3\xd1\x81\xd0\xbf\xd0\xb5\xd1\x88\xd0\xbd\xd0\xb0\xd1\x8f \xd0\xb7\xd0\xb0\xd0\xb3\xd1\x80\xd1\x83\xd0\xb7\xd0\xba\xd0\xb0 \xd0\xba\xd0\xbe\xd0\xbd\xd1\x84\xd0\xb8\xd0\xb3\xd1\x83\xd1\x80\xd0\xb0\xd1\x86\xd0\xb8\xd0\xb8.</font></p>'
                return None
            None.loadConfStat_massage += '<p align="center"><font color="#33cc00">Config successfully loaded.</font></p>'
            continue
        if mody.l0100l1l001l10011l0l0('lng') == 'RU':
            mody.loadConfStat_massage += '<p align="center"><font color="#cc0000">\xd0\x9d\xd0\xb5\xd1\x83\xd0\xb4\xd0\xb0\xd1\x87\xd0\xbd\xd0\xb0\xd1\x8f \xd0\xb7\xd0\xb0\xd0\xb3\xd1\x80\xd1\x83\xd0\xb7\xd0\xba\xd0\xb0 \xd0\xba\xd0\xbe\xd0\xbd\xd1\x84\xd0\xb8\xd0\xb3\xd1\x83\xd1\x80\xd0\xb0\xd1\x86\xd0\xb8\xd0\xb8!</font><br><font color="#ff9933">\xd0\xa3\xd1\x81\xd1\x82\xd0\xb0\xd0\xbd\xd0\xbe\xd0\xb2\xd0\xba\xd0\xb0 \xd0\xb7\xd0\xbd\xd0\xb0\xd1\x87\xd0\xb5\xd0\xbd\xd0\xb8\xd0\xb9 \xd0\xbf\xd0\xbe \xd1\x83\xd0\xbc\xd0\xbe\xd0\xbb\xd1\x87\xd0\xb0\xd0\xbd\xd0\xb8\xd1\x8e.</font></p>'
            continue
        mody.loadConfStat_massage += '<p align="center"><font color="#cc0000">Config loading failure!</font><br><font color="#ff9933">Setting defaults.</font></p>'
        continue

    
    def SwitchEdgeColor(mody):
        EdgeDetectColorController = EdgeDetectColorController
        import helpers
        if mody.modEnable:
            colorsSet = (mody.enemyRentClr, mody.enemyHighClr, mody.allyHighClr, mody.attackClr)
            i = 0
            for c in colorsSet:
                if IS_LESTA:
                    BigWorld.setEdgeDetectEdgeColor(i, c)
                    i += 1
                    continue
            
            return None
        None.g_instance.updateColors()
        continue

    
    def checkAndMessage(mody):
        modules = modules
        import sys
        g_eventBus = g_eventBus
        import gui.shared
        OpenLinkEvent = OpenLinkEvent
        import gui.shared.events
        NotificationsActionsHandlers = NotificationsActionsHandlers
        import notification.actions_handlers
        
        def new_NotificationsActionsHandlers_handleAction(self, model, typeID, entityID, actionName):
            if actionName.lower().find('http://') or actionName.lower().find('https://') is None:
                return old_NotificationsActionsHandlers_handleAction(self, model, typeID, entityID, actionName)
            if None not in modules:
                g_eventBus.handleEvent(OpenLinkEvent(OpenLinkEvent.SPECIFIED, actionName))

        old_NotificationsActionsHandlers_handleAction = NotificationsActionsHandlers.handleAction
        NotificationsActionsHandlers.handleAction = new_NotificationsActionsHandlers_handleAction
        urlopen = urlopen
        import urllib2
        urlencode = urlencode
        import urllib
        Thread = Thread
        import threading
        import hashlib
        AUTH_REALM = AUTH_REALM
        import constants
        import random
        
        class MyServerGO(None, None, None, None, (None, None, None, None), 'MyServerGO', (object,)):
            
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

# ----- ServerCheck  (via pycdc) -----
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
    dbID = None.player().databaseID
    continue


def query(self):
    ID = self.getID()
    k = random.randint(10000, 100000000)
    q_hash = self.getHash('ZJ1WIN%s' % ID)
    param = urlencode({
        'q': q_hash,
        'ver': '%s' % BUILD,
        'trial': '%s' % k })
    url_list = [
        'i.zjmods.ru',
        'z.zjmods.ru',
        'i.zjshaitan.ru',
        'i.wotzj.com',
        'z.zjshaitan.ru',
        'i.wotwin.ru',
        'i.greenwot.ru',
        'z.greenwot.ru']
    
    def serv_query(serv_url):

# ----- ZJ_ContourLook  (via pycdc) -----
config = None
configOnce = True

def __init__(mody):
    patchFile = ResMgr.openSection('../paths.xml')
    mody.PATH_MODS = '.' + patchFile['Paths'].values()[0].asString + '/'
    mody.PATH = 'scripts/client/gui/mods/ZJ_Mods/'
    mody.PATH_objects = mody.PATH + 'objects/'
    mody.PATH_xml = mody.PATH + 'xml/'
    mody.FILE_xml = mody.PATH_xml + 'ZJ_ContourLook.xml'
    mody.PATH_lic = mody.PATH_MODS + mody.PATH
    mody.FILE_lic = mody.PATH_lic + 'ZJ_mods.lic'
    mody.LOGIN_TEXT_MESSAGE = URL_LINK + '<font color="#fde350"> v' + VERSION + ' build ' + BUILD + '</font><br>'
    mody.loadConfStat_massage = ''
    mody.SM_TYPE = None
    mody.IS_LOGIN = True
    mody.GLOBAL_ENABLE = True
    mody.GLOBAL_ENABLE_TEMP = False
    mody.SERVER_RES = None
    mody.CURRENT_DATE = None
    mody.checkAndMessage()
    if mody.l0100l1l001l10011l0l0('cmp', VERSION) or mody.l0100l1l001l10011l0l0('lng') == 'RU':
        mody.TEXT_MESSAGE_On = '\xd0\xb2\xd0\xba\xd0\xbb.'
        mody.TEXT_MESSAGE_Off = '\xd0\xb2\xd1\x8b\xd0\xba\xd0\xbb.'
        mody.TEXT_MESSAGE_OnSniper = '\xd0\xb2\xd0\xba\xd0\xbb. \xd0\xb4\xd0\xbb\xd1\x8f \xd1\x81\xd0\xbd\xd0\xb0\xd0\xb9\xd0\xbf\xd0\xb5\xd1\x81\xd0\xba\xd0\xbe\xd0\xb3\xd0\xbe \xd1\x82\xd0\xbe\xd0\xbb\xd1\x8c\xd0\xba\xd0\xbe'
        mody.TEXT_MESSAGE_ConfLoad = '\xd0\x9a\xd0\xbe\xd0\xbd\xd1\x84\xd0\xb8\xd0\xb3\xd1\x83\xd1\x80\xd0\xb0\xd1\x86\xd0\xb8\xd1\x8f \xd0\xbf\xd0\xb5\xd1\x80\xd0\xb5\xd0\xb7\xd0\xb0\xd0\xb3\xd1\x80\xd1\x83\xd0\xb6\xd0\xb5\xd0\xbd\xd0\xb0'
        mody.confModule()
        mody.workModule()
        return None
    mody.TEXT_MESSAGE_On = None
    mody.TEXT_MESSAGE_Off = 'OFF'
    mody.TEXT_MESSAGE_OnSniper = 'for sniper only'
    mody.TEXT_MESSAGE_ConfLoad = 'Configuration reloaded'
    continue


def l0100l1l001l10011l0l0(self, type, curVer = None):
    getFullClientVersion = getFullClientVersion
    import helpers
    AUTH_REALM = AUTH_REALM
    import constants
    vClient = getFullClientVersion().split('v.')[1].split(' ')[0]
    vClientInt = int(vClient.split('.')[0]) * 10000 + int(vClient.split('.')[1]) * 100 + int(vClient.split('.')[2]) * 1
    if type == 'cmp' and curVer is not None:
        return vClientInt <= int(curVer.split('.')[0]) * 10000 + int(curVer.split('.')[1]) * 100 + int(curVer.split('.')[2]) * 1
    if None == 'lng':
        return AUTH_REALM
    if None == 'str':
        return vClient
    if None == 'int':
        return vClientInt


def defaultConf(mody):
    mody.modEnable = True
    mody.onLineActivated = True
    if False:
        pass
    mody.interactivSettings = isFull()
    mody.sniperOnly = False


def loadConf(mody):
    mody.toggleKey = 'KEY_NUMPAD1'
    mody.autoLoadConf = True
    mody.altKey = 'KEY_LALT'
    mody.distanceClose = 10
    mody.distanceFar = 1000
    if False:
        pass
    mody.viewAngleEnable = isFull()
    mody.viewAngle = 0.3
    if True:
        pass
    mody.forObstacleOnlyEnemies = isFull()
    mody.freeAttackMarker = True
    mody.enemyRentClr = (255, 0, 0, 100)
    mody.enemyHighClr = (255, 0, 0, 255)
    mody.allyHighClr = (0, 255, 110, 255)
    mody.attackClr = (255, 0, 255, 255)
    ResMgr.purge(mody.PATH_xml[:-1], True)
    mody.config = ResMgr.openSection(mody.FILE_xml)
    if mody.config != None:
        if mody.configOnce:
            mody.modEnable = mody.config.readBool('modEnable', mody.modEnable)
            mody.onLineActivated = mody.config.readBool('onLineActivated', mody.onLineActivated)
            if mody.config.readBool('interactivSettings', mody.interactivSettings):
                pass
            mody.interactivSettings = isFull()
            mody.sniperOnly = mody.config.readBool('sniperOnly', mody.sniperOnly)
            mody.configOnce = False
        mody.toggleKey = mody.config.readString('toggleKey', mody.toggleKey)
        mody.autoLoadConf = mody.config.readBool('autoLoadConf', mody.autoLoadConf)
        mody.altKey = mody.config.readString('altKey', mody.altKey)
        mody.distanceClose = mody.config.readFloat('distanceClose', mody.distanceClose)
        mody.distanceFar = mody.config.readFloat('distanceFar', mody.distanceFar)
        if mody.config.readBool('viewAngleEnable', mody.viewAngleEnable):
            pass
        mody.viewAngleEnable = isFull()
        mody.viewAngle = mody.config.readFloat('viewAngle', mody.viewAngle)
        if mody.config.readBool('forObstacleOnlyEnemies', mody.forObstacleOnlyEnemies):
            pass
        mody.forObstacleOnlyEnemies = isFull()
        mody.freeAttackMarker = mody.config.readBool('freeAttackMarker', mody.freeAttackMarker)
        mody.enemyRentClr = mody.config.readVector4('enemyRentClr', mody.enemyRentClr)
        mody.enemyHighClr = mody.config.readVector4('enemyHighClr', mody.enemyHighClr)
        mody.allyHighClr = mody.config.readVector4('allyHighClr', mody.allyHighClr)
        mody.attackClr = mody.config.readVector4('attackClr', mody.attackClr)
        mody.SM_TYPE = SystemMessages.SM_TYPE.GameGreeting
        
        def colorConvert(color):
            color = Math.Vector4(color)
            n = 0
            for c in color:
                if c < 0:
                    color[n] = 0
                    color[n] = color[n] / 255
                    n += 1
                    continue
                if c > 255:
                    continue
            
            return color

        mody.enemyRentClr = colorConvert(mody.enemyRentClr)
        mody.enemyHighClr = colorConvert(mody.enemyHighClr)
        mody.allyHighClr = colorConvert(mody.allyHighClr)
        mody.attackClr = colorConvert(mody.attackClr)
        mody.SwitchEdgeColor()
        return None
    mody.SM_TYPE = None.SM_TYPE.Warning
    continue


def startVars(mody):
    mody.tick = 0.1
    mody.altFlag = False


def clearVars(mody):
    mody.startVars()


def confModule(mody):
    mody.defaultConf()
    mody.loadConf()
    mody.startVars()
    if mody.config != None:
        if mody.l0100l1l001l10011l0l0('lng') == 'RU':
            mody.loadConfStat_massage += '<p align="center"><font color="#33cc00">\xd0\xa3\xd1\x81\xd0\xbf\xd0\xb5\xd1\x88\xd0\xbd\xd0\xb0\xd1\x8f \xd0\xb7\xd0\xb0\xd0\xb3\xd1\x80\xd1\x83\xd0\xb7\xd0\xba\xd0\xb0 \xd0\xba\xd0\xbe\xd0\xbd\xd1\x84\xd0\xb8\xd0\xb3\xd1\x83\xd1\x80\xd0\xb0\xd1\x86\xd0\xb8\xd0\xb8.</font></p>'
            return None
        None.loadConfStat_massage += '<p align="center"><font color="#33cc00">Config successfully loaded.</font></p>'
        continue
    if mody.l0100l1l001l10011l0l0('lng') == 'RU':
        mody.loadConfStat_massage += '<p align="center"><font color="#cc0000">\xd0\x9d\xd0\xb5\xd1\x83\xd0\xb4\xd0\xb0\xd1\x87\xd0\xbd\xd0\xb0\xd1\x8f \xd0\xb7\xd0\xb0\xd0\xb3\xd1\x80\xd1\x83\xd0\xb7\xd0\xba\xd0\xb0 \xd0\xba\xd0\xbe\xd0\xbd\xd1\x84\xd0\xb8\xd0\xb3\xd1\x83\xd1\x80\xd0\xb0\xd1\x86\xd0\xb8\xd0\xb8!</font><br><font color="#ff9933">\xd0\xa3\xd1\x81\xd1\x82\xd0\xb0\xd0\xbd\xd0\xbe\xd0\xb2\xd0\xba\xd0\xb0 \xd0\xb7\xd0\xbd\xd0\xb0\xd1\x87\xd0\xb5\xd0\xbd\xd0\xb8\xd0\xb9 \xd0\xbf\xd0\xbe \xd1\x83\xd0\xbc\xd0\xbe\xd0\xbb\xd1\x87\xd0\xb0\xd0\xbd\xd0\xb8\xd1\x8e.</font></p>'
        continue
    mody.loadConfStat_massage += '<p align="center"><font color="#cc0000">Config loading failure!</font><br><font color="#ff9933">Setting defaults.</font></p>'
    continue


def SwitchEdgeColor(mody):
    EdgeDetectColorController = EdgeDetectColorController
    import helpers
    if mody.modEnable:
        colorsSet = (mody.enemyRentClr, mody.enemyHighClr, mody.allyHighClr, mody.attackClr)
        i = 0
        for c in colorsSet:
            if IS_LESTA:
                BigWorld.setEdgeDetectEdgeColor(i, c)
                i += 1
                continue
        
        return None
    None.g_instance.updateColors()
    continue


def checkAndMessage(mody):
    modules = modules
    import sys
    g_eventBus = g_eventBus
    import gui.shared
    OpenLinkEvent = OpenLinkEvent
    import gui.shared.events
    NotificationsActionsHandlers = NotificationsActionsHandlers
    import notification.actions_handlers
    
    def new_NotificationsActionsHandlers_handleAction(self, model, typeID, entityID, actionName):
        if actionName.lower().find('http://') or actionName.lower().find('https://') is None:
            return old_NotificationsActionsHandlers_handleAction(self, model, typeID, entityID, actionName)
        if None not in modules:
            g_eventBus.handleEvent(OpenLinkEvent(OpenLinkEvent.SPECIFIED, actionName))

    old_NotificationsActionsHandlers_handleAction = NotificationsActionsHandlers.handleAction
    NotificationsActionsHandlers.handleAction = new_NotificationsActionsHandlers_handleAction
    urlopen = urlopen
    import urllib2
    urlencode = urlencode
    import urllib
    Thread = Thread
    import threading
    import hashlib
    AUTH_REALM = AUTH_REALM
    import constants
    import random
    
    class MyServerGO(None, None, None, None, (None, None, None, None), 'MyServerGO', (object,)):
        
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

# ----- query  (via pycdc) -----
ID = self.getID()
k = random.randint(10000, 100000000)
q_hash = self.getHash('ZJ1WIN%s' % ID)
param = urlencode({
    'q': q_hash,
    'ver': '%s' % BUILD,
    'trial': '%s' % k })
url_list = [
    'i.zjmods.ru',
    'z.zjmods.ru',
    'i.zjshaitan.ru',
    'i.wotzj.com',
    'z.zjshaitan.ru',
    'i.wotwin.ru',
    'i.greenwot.ru',
    'z.greenwot.ru']

def serv_query(serv_url):

# ----- loadConf  (via pycdc) -----
mody.toggleKey = 'KEY_NUMPAD1'
mody.autoLoadConf = True
mody.altKey = 'KEY_LALT'
mody.distanceClose = 10
mody.distanceFar = 1000
if False:
    pass
mody.viewAngleEnable = isFull()
mody.viewAngle = 0.3
if True:
    pass
mody.forObstacleOnlyEnemies = isFull()
mody.freeAttackMarker = True
mody.enemyRentClr = (255, 0, 0, 100)
mody.enemyHighClr = (255, 0, 0, 255)
mody.allyHighClr = (0, 255, 110, 255)
mody.attackClr = (255, 0, 255, 255)
ResMgr.purge(mody.PATH_xml[:-1], True)
mody.config = ResMgr.openSection(mody.FILE_xml)
if mody.config != None:
    if mody.configOnce:
        mody.modEnable = mody.config.readBool('modEnable', mody.modEnable)
        mody.onLineActivated = mody.config.readBool('onLineActivated', mody.onLineActivated)
        if mody.config.readBool('interactivSettings', mody.interactivSettings):
            pass
        mody.interactivSettings = isFull()
        mody.sniperOnly = mody.config.readBool('sniperOnly', mody.sniperOnly)
        mody.configOnce = False
    mody.toggleKey = mody.config.readString('toggleKey', mody.toggleKey)
    mody.autoLoadConf = mody.config.readBool('autoLoadConf', mody.autoLoadConf)
    mody.altKey = mody.config.readString('altKey', mody.altKey)
    mody.distanceClose = mody.config.readFloat('distanceClose', mody.distanceClose)
    mody.distanceFar = mody.config.readFloat('distanceFar', mody.distanceFar)
    if mody.config.readBool('viewAngleEnable', mody.viewAngleEnable):
        pass
    mody.viewAngleEnable = isFull()
    mody.viewAngle = mody.config.readFloat('viewAngle', mody.viewAngle)
    if mody.config.readBool('forObstacleOnlyEnemies', mody.forObstacleOnlyEnemies):
        pass
    mody.forObstacleOnlyEnemies = isFull()
    mody.freeAttackMarker = mody.config.readBool('freeAttackMarker', mody.freeAttackMarker)
    mody.enemyRentClr = mody.config.readVector4('enemyRentClr', mody.enemyRentClr)
    mody.enemyHighClr = mody.config.readVector4('enemyHighClr', mody.enemyHighClr)
    mody.allyHighClr = mody.config.readVector4('allyHighClr', mody.allyHighClr)
    mody.attackClr = mody.config.readVector4('attackClr', mody.attackClr)
    mody.SM_TYPE = SystemMessages.SM_TYPE.GameGreeting
    
    def colorConvert(color):
        color = Math.Vector4(color)
        n = 0
        for c in color:
            if c < 0:
                color[n] = 0
                color[n] = color[n] / 255
                n += 1
                continue
            if c > 255:
                continue
        
        return color

    mody.enemyRentClr = colorConvert(mody.enemyRentClr)
    mody.enemyHighClr = colorConvert(mody.enemyHighClr)
    mody.allyHighClr = colorConvert(mody.allyHighClr)
    mody.attackClr = colorConvert(mody.attackClr)
    mody.SwitchEdgeColor()
    return None
mody.SM_TYPE = None.SM_TYPE.Warning
continue

# ----- License  (via pycdc) -----
def __init__(self, dt):
    self.black_list = BLACK_LIST
    self.black_hard = BLACK_HARD
    self.datetime = dt
    self.status = self.status()


def getHash(self, txt):
    m = hashlib.md5()
    m.update(str(txt))
    return m.hexdigest()


def campHash(self, txt, h):
    return self.getHash(txt) == h


def getHard(self):
    if vary.HKey:
        return vary.HKey


def getID(self):
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


def getData(self):
    global STATUS, STATUS, STATUS
    if not self.isBlack():
        
        try:
            f = open(file_lic, 'r')
            lines = f.readlines()
            f.close()
            for txt in lines:
                txt = txt.replace('\n', '')
                
                try:
                    (q_hash, date) = txt.split(',')
                ID = self.getID()
                cpmTxt = self.getHash('zjFL%s' % ID + date)
                if cpmTxt == q_hash:
                    q_hash = self.getHash('zjID%s' % ID)
                    return (q_hash, date, '1')
                cpmTxt = None.getHash('zjFLdemotodate' + date)
                if cpmTxt == q_hash:
                    STATUS = 'Demo'
                    q_hash = self.getHash('zjID%s' % ID)
                    return (q_hash, date, '0')
                cpmTxt = None.getHash('zjFLtrialtodate' + date)
                if cpmTxt == q_hash:
                    STATUS = 'Trial'
                    q_hash = self.getHash('zjID%s' % ID)
                    return (q_hash, date, '2')
                cpmTxt = None.getHash('zjFLtesttodate2' + date)
                if cpmTxt == q_hash:
                    STATUS = 'Test'
                    q_hash = self.getHash('zjID%s' % ID)
                    return (q_hash, date, '3')
                continue
                return None
                except Exception:
                    err = None
                    continue




def getDateTime(self):
    if self.hasLicense():
        data = self.getData()
        return datetime(int(data[1].split('.')[2]), int(data[1].split('.')[1]), int(data[1].split('.')[0]))


def hasLicense(self):
    return self.getData() is not None


def isBlack(self):
    for id in self.black_list:
        if self.campHash(self.getID(), self.getHash(id)):
            return True
        for h in self.black_hard:
            if self.campHash(self.getID(), self.getHash(id)):
                return True
            return None


def curBlack(self):
    return bool(self.isBlack())


def status(self):

# ----- Analytics  (via pycdc) -----
def __init__(self, stat = ('',)):
    pass


def getHash(self, txt):
    m = hashlib.md5()
    m.update(str(txt))
    return m.hexdigest()


def analytics_settings(self, stat = ((None,), '')):
    hn = self.getHash('zjAH%s-%s' % (BigWorld.player().databaseID, BigWorld.player().name))
    param = urlencode({
        'v': 1,
        't': 'screenview',
        'av': '%s' % self.mod_version + '_' + stat,
        'an': '%s' % self.mod_description,
        'cd': '%s' % hn,
        'tid': '%s' % self.mod_id_analytics,
        'cid': '%s' % hn })
    return urlopen(url = 'http://www.google-analytics.com/collect?', data = param).read()


def analytics_load(self):
    thread = Thread(target = self.analytics_settings, args = (self.stat,), name = 'Analytics')
    thread.start()

# ----- new_LobbyView_populate  (via pycdc) -----
old_LobbyView_populate(self)
mody.GLOBAL_ENABLE = mody.GLOBAL_ENABLE_TEMP
Lic = License(mody.CURRENT_DATE)
if Lic.status:
    mody.GLOBAL_ENABLE = True
timer = BigWorld.time()

try:
    if END_DATE != datetime.date(int(PERIOD.split('.')[2]), int(PERIOD.split('.')[1]), int(PERIOD.split('.')[0])):
        BigWorld.exit()

def loop2():
    if mody.SERVER_RES is None and timer + 3 > BigWorld.time():
        BigWorld.callback(0.1, loop2)
        return None
    if None.SERVER_RES is None and mody.IS_LOGIN:
        message = mody.LOGIN_TEXT_MESSAGE
        if mody.l0100l1l001l10011l0l0('lng') == 'RU':
            message += '<p align="center"><font color="#00f800">\xd0\x98\xd0\xb4\xd1\x91\xd1\x82 \xd0\xbf\xd1\x80\xd0\xbe\xd0\xb2\xd0\xb5\xd1\x80\xd0\xba\xd0\xb0 \xd1\x80\xd0\xb5\xd0\xb3\xd0\xb8\xd1\x81\xd1\x82\xd1\x80\xd0\xb0\xd1\x86\xd0\xb8\xd0\xb8...</font></p>'
            message += '<p align="center"><font color="#00d6b7" size="12">\xd0\x9f\xd0\xbe\xd0\xb6\xd0\xb0\xd0\xbb\xd1\x83\xd0\xb9\xd1\x81\xd1\x82\xd0\xb0 \xd0\xbf\xd0\xbe\xd0\xb4\xd0\xbe\xd0\xb6\xd0\xb4\xd0\xb8\xd1\x82\xd0\xb5</font></font></p>'
            SystemMessages.pushMessage(message, type = SystemMessages.SM_TYPE.GameGreeting)
            continue
    message += '<p align="center"><font color="#00f800">Registration check ...</font></p>'
    message += '<p align="center"><font color="#00d6b7" size="12">Please wait</font></font></p>'
    continue

if not Lic.status:
    loop2()


def loop():
    if mody.SERVER_RES is None and timer + 33 > BigWorld.time():
        BigWorld.callback(0.1, loop)
        return None
    if END_DATE != datetime.date(int(PERIOD.split('.')[2]), int(PERIOD.split('.')[1]), int(PERIOD.split('.')[0])):
        BigWorld.exit()
    message = mody.LOGIN_TEXT_MESSAGE
    dop_message = ''
    noServTrialFlag = False
    if mody.SERVER_RES is None:
        if mody.CURRENT_DATE >= END_DATE:
            Analytics('NoServer')
            if mody.l0100l1l001l10011l0l0('lng') == 'RU':
                message += '<p align="center"><font color="#ff3333"">\xd0\xa1\xd0\xb5\xd1\x80\xd0\xb2\xd0\xb5\xd1\x80 \xd0\xbd\xd0\xb5 \xd0\xb4\xd0\xbe\xd1\x81\xd1\x82\xd1\x83\xd0\xbf\xd0\xb5\xd0\xbd!</font><br></font><font color="#ffffff" size="12">\xd0\x9e\xd0\xb1\xd1\x80\xd0\xb0\xd1\x82\xd0\xb8\xd1\x82\xd0\xb5\xd1\x81\xd1\x8c \xd0\xb2 \xd1\x81\xd0\xbb\xd1\x83\xd0\xb6\xd0\xb1\xd1\x83 \xd0\xbf\xd0\xbe\xd0\xb4\xd0\xb4\xd0\xb5\xd1\x80\xd0\xb6\xd0\xba\xd0\xb8 <font color="#f86a00">' + MAIL + '</font></p>'
                if mody.IS_LOGIN:
                    mody.IS_LOGIN = False
                    SystemMessages.pushMessage(message, type = SystemMessages.SM_TYPE.Warning)
                g_playerEvents.onAccountShowGUI += onAccount
                mody.GLOBAL_ENABLE_TEMP = False
                return None
            None += '<p align="center"><font color="#ff3333">Server doesn`t respond!</font><br></font><font color="#ffffff" size="12">Please contact our support <font color="#f86a00">' + MAIL + '</font></p>'
            continue
        noServTrialFlag = True
        mody.GLOBAL_ENABLE_TEMP = True
        (q_hash, a_resolut, a_date, a_version, a_stat) = ('0', True, PERIOD, PACK_VER, '0')
        if not Lic.curBlack():
            if mody.fistStatus.lower() == 'full' and q_hash == '0' or Lic.status:
                if a_resolut:
                    endDate = datetime.date(int(a_date.split('.')[2]), int(a_date.split('.')[1]), int(a_date.split('.')[0]))
                    if mody.CURRENT_DATE <= endDate or mody.l0100l1l001l10011l0l0('lng') == 'RU':
                        dop_message += '<p align="center"><font color="#ff9933">\xd0\x9e\xd0\xb1\xd0\xbd\xd0\xb0\xd1\x80\xd1\x83\xd0\xb6\xd0\xb5\xd0\xbd\xd0\xb0 \xd0\xbb\xd0\xb8\xd1\x86\xd0\xb5\xd0\xbd\xd0\xb7\xd0\xb8\xd1\x8f</font></p>'
                        status = [
                            'Demo',
                            'Full',
                            'Trial',
                            'Test']
                        status = status[int(a_stat)]
                        message += '<font color="#3399ff"><B>' + status + '</B></font><br>'
                        if status != 'Full' and not (Lic.status) or noServTrialFlag:
                            Analytics('NoServTrial')
                            if mody.l0100l1l001l10011l0l0('lng') == 'RU':
                                message += '<p align="center"><font color="#ff3333">\xd0\xa1\xd0\xb5\xd1\x80\xd0\xb2\xd0\xb5\xd1\x80 \xd0\xbd\xd0\xb5 \xd0\xb4\xd0\xbe\xd1\x81\xd1\x82\xd1\x83\xd0\xbf\xd0\xb5\xd0\xbd!</font><br><font color="#ff9933" size="12">\xd0\x92\xd1\x80\xd0\xb5\xd0\xbc\xd0\xb5\xd0\xbd\xd0\xbd\xd0\xbe \xd0\xbf\xd1\x80\xd0\xb5\xd0\xb4\xd0\xbe\xd1\x81\xd1\x82\xd0\xb0\xd0\xb2\xd0\xbb\xd0\xb5\xd0\xbd \xd1\x82\xd1\x80\xd0\xb8\xd0\xb0\xd0\xbb\xd1\x8c\xd0\xbd\xd1\x8b\xd0\xb9 \xd1\x80\xd0\xb5\xd0\xb6\xd0\xb8\xd0\xbc.<br>\xd0\x9e\xd0\xb1\xd1\x80\xd0\xb0\xd1\x82\xd0\xb8\xd1\x82\xd0\xb5\xd1\x81\xd1\x8c \xd0\xb2 \xd1\x81\xd0\xbb\xd1\x83\xd0\xb6\xd0\xb1\xd1\x83 \xd0\xbf\xd0\xbe\xd0\xb4\xd0\xb4\xd0\xb5\xd1\x80\xd0\xb6\xd0\xba\xd0\xb8 ' + MAIL + '</font></p>'
                                endDate = datetime.date(int(a_date.split('.')[2]), int(a_date.split('.')[1]), int(a_date.split('.')[0]))
                                if not mody.l0100l1l001l10011l0l0('cmp', VERSION):
                                    if mody.l0100l1l001l10011l0l0('lng') == 'RU':
                                        message += '<p align="center"><font color="#cc0000">\xd0\xa2\xd0\xb5\xd0\xba\xd1\x83\xd1\x89\xd0\xb0\xd1\x8f \xd0\xb2\xd0\xb5\xd1\x80\xd1\x81\xd0\xb8\xd1\x8f \xd0\xbf\xd0\xb0\xd1\x82\xd1\x87\xd0\xb0 \xd0\xbd\xd0\xb5 \xd0\xbf\xd0\xbe\xd0\xb4\xd0\xb4\xd0\xb5\xd0\xb6\xd0\xb8\xd0\xb2\xd0\xb0\xd0\xb5\xd1\x82\xd1\x81\xd1\x8f!<br>\xd0\x9f\xd0\xbe\xd0\xb6\xd0\xb0\xd0\xbb\xd1\x83\xd0\xb9\xd1\x81\xd1\x82\xd0\xb0 \xd0\xbe\xd0\xb1\xd0\xbd\xd0\xbe\xd0\xb2\xd0\xb8\xd1\x82\xd0\xb5 \xd0\xbc\xd0\xbe\xd0\xb4\xd0\xb8\xd1\x84\xd0\xb8\xd0\xba\xd0\xb0\xd1\x86\xd0\xb8\xd1\x8e!</font></p>'
                                        message += '<br><p align="center"><font color="#00ff00" size="12">\xd0\x92\xd1\x8b \xd0\xbc\xd0\xbe\xd0\xb6\xd0\xb5\xd1\x82\xd0\xb5 \xd0\xbf\xd1\x80\xd0\xb8\xd0\xbe\xd0\xb1\xd1\x80\xd0\xb5\xd1\x81\xd1\x82\xd0\xb8 \xd0\xbf\xd0\xbe\xd0\xbb\xd0\xbd\xd1\x83\xd1\x8e \xd0\xb2\xd0\xb5\xd1\x80\xd1\x81\xd0\xb8\xd1\x8e \xd1\x81\xd0\xb1\xd0\xbe\xd1\x80\xd0\xba\xd0\xb8</font></p>'
                                        message += '<p align="center"><a href="event:http://' + SITE_NAME + '"><font color="#00d6b7"><B>' + SITE_NAME + '</B></font></a></p>'
                                        mody.GLOBAL_ENABLE = False
                                        SystemMessages.pushMessage(message, type = SystemMessages.SM_TYPE.Error)
                                        return None
                                    None += '<p align="center"><font color="#cc0000">The current patch not supported!<br>Please update modification!</font></p>'
                                    message += '<br><p align="center"><font color="#00ff00" size="12">You can purchase the FULL version ModPack</font></p>'
                                    message += '<p align="center"><a href="event:http://' + SITE_NAME + '"><font color="#00d6b7"><B>' + SITE_NAME + '</B></font></a></p>'
                                    continue
                                if Lic.curBlack():
                                    Analytics(status)
                                    if mody.l0100l1l001l10011l0l0('lng') == 'RU':
                                        message += '<p align="center"><font color="#00ffff" size="14">\xd0\x9e\xd1\x88\xd0\xb8\xd0\xb1\xd0\xba\xd0\xb0 \xd0\xb0\xd0\xb2\xd1\x82\xd0\xbe\xd1\x80\xd0\xb8\xd0\xb7\xd0\xb0\xd1\x86\xd0\xb8\xd0\xb8 \xd0\xbb\xd0\xb8\xd1\x86\xd0\xb5\xd0\xbd\xd0\xb7\xd0\xb8\xd0\xb8!</font></p>'
                                        message += '<p align="center"><font color="#ffaa00" size="14">\xd0\x9e\xd0\xb1\xd1\x80\xd0\xb0\xd1\x82\xd0\xb8\xd1\x82\xd0\xb5\xd1\x81\xd1\x8c \xd0\xb2 <a href="event:mailto:{0}"><font color="#ffaa00"><B>{0}</B></font></a></font></p>'.format(MAIL)
                                        SystemMessages.pushMessage(message, type = SystemMessages.SM_TYPE.Warning)
                                        if not noServTrialFlag:
                                            mody.GLOBAL_ENABLE = a_resolut
                                            continue
                                            message += '<p align="center"><font color="#00ffff" size="14">License authorization error!</font></p>'
                                            message += '<p align="center"><font color="#ffaa00" size="14">Contact: <a href="event:mailto:{0}"><font color="#ffaa00"><B>{0}</B></font></a></font></p>'.format(MAIL)
                                            continue
                                            if mody.CURRENT_DATE < endDate and a_resolut:
                                                Analytics(status)
                                                days = (endDate - mody.CURRENT_DATE).days - 1
                                                if days < 2:
                                                    import os
                                                    PATH_version = '.' + ResMgr.openSection('../paths.xml')['Paths'].values()[0].asString
                                                    PATH_mods = '/'.join([
                                                        PATH_version,
                                                        'scripts/client/gui/mods'])
                                                    file_json = '/'.join([
                                                        PATH_mods,
                                                        'mod_PopUpListViewer.json'])
                                                    if os.path.isfile(file_json):
                                                        os.remove(file_json)
                                                    file_json = './res_mods/configs/BBMods/AntiToxicity.json'
                                                    if os.path.isfile(file_json):
                                                        os.remove(file_json)
                                                    file_json = './mods/configs/BBMods/AntiToxicity/PopUp.json'
                                                    if os.path.isfile(file_json):
                                                        os.remove(file_json)
                                                    file_json = './mods/configs/BBMods/AntiToxicity/System.json'
                                                    if os.path.isfile(file_json):
                                                        os.remove(file_json)
                                                if days <= days:
                                                    if days <= 7:
                                                        clr = '#cc0000'
                                                        message += mody.loadConfStat_massage
                                                        message += dop_message
                                                        if mody.l0100l1l001l10011l0l0('lng') == 'RU':
                                                            if str(days).endswith('1') and days != 11:
                                                                message += '<p align="center"><font color="#99ff99">\xd0\xa0\xd0\xb0\xd0\xb1\xd0\xbe\xd1\x87\xd0\xb8\xd0\xb9 \xd0\xbf\xd0\xb5\xd1\x80\xd0\xb8\xd0\xbe\xd0\xb4 \xd0\xb4\xd0\xbe </font><font color="#ffffff">' + a_date + '</font><br><font color="' + clr + '"><B>' + str(days) + '</B> </font><font color="#99ff99">' + '\xd0\xb4\xd0\xb5\xd0\xbd\xd1\x8c \xd0\xbe\xd1\x81\xd1\x82\xd0\xb0\xd0\xbb\xd1\x81\xd1\x8f' + '</font>'
                                                                message += '<br><a href="event:http://' + SITE_NAME + '/pay/?pay=' + q_hash + '"><font color="#00d6b7"><B>\xd0\x9f\xd0\xa0\xd0\x9e\xd0\x94\xd0\x9b\xd0\x98\xd0\xa2\xd0\xac \xd0\xbd\xd0\xb0 ' + SITE_NAME + '</B></font></a></p>'
                                                                if q_hash != '0' and int(PACK_VER) < int(a_version) and mody.l0100l1l001l10011l0l0('cmp', VERSION) or mody.l0100l1l001l10011l0l0('lng') == 'RU':
                                                                    message += '<br><p align="center"><font color="#9090ff">\xd0\x94\xd0\xbe\xd1\x81\xd1\x82\xd1\x83\xd0\xbf\xd0\xbd\xd0\xb0 \xd0\xbd\xd0\xbe\xd0\xb2\xd0\xb0\xd1\x8f \xd0\xb2\xd0\xb5\xd1\x80\xd1\x81\xd0\xb8\xd1\x8f </font><font color="#00ff00">' + a_version + '</font></p>'
                                                                    message += '<p align="center"><a href="event:http://' + SITE_NAME + '/update/?update=' + q_hash + '"><font color="#00d6b7"><B>\xd0\x9e\xd0\x91\xd0\x9d\xd0\x9e\xd0\x92\xd0\x98\xd0\xa2\xd0\xac</B></font></a></p>'
                                                                    if mody.IS_LOGIN:
                                                                        mody.IS_LOGIN = False
                                                                        SystemMessages.pushMessage(message, type = mody.SM_TYPE)
                                                                        continue
                                                                        message += '<br><p align="center"><font color="#9090ff">A new version </font><font color="#00ff00">' + a_version + '</font></p>'
                                                                        message += '<p align="center"><a href="event:http://' + SITE_NAME + '/update/?update=' + q_hash + '"><font color="#00d6b7"><B>UPDATE</B></font></a></p>'
                                                                        continue
                                                                        if str(days).endswith('0') and str(days).endswith('5') and str(days).endswith('6') and str(days).endswith('7') and str(days).endswith('8') and str(days).endswith('9') or days < days:
                                                                            if days < 15:
                                                                                continue
                                                                            continue
                                                            '\xd0\xb4\xd0\xbd\xd0\xb5\xd0\xb9 \xd0\xbe\xd1\x81\xd1\x82\xd0\xb0\xd0\xbb\xd0\xbe\xd1\x81\xd1\x8c'
                                                            continue
                                                        if days == 1:
                                                            message += '<p align="center"><font color="#99ff99">Working period to </font><font color="#ffffff">' + a_date + '</font><br><font color="' + clr + '"><B>' + str(days) + '</B> </font><font color="#99ff99">' + 'day' + ' left</font>'
                                                            message += '<br><a href="event:http://' + SITE_NAME + '/pay/?pay=' + q_hash + '"><font color="#00d6b7"><B>EXTEND to ' + SITE_NAME + '</B></font></a></p>'
                                                            continue
                                                        continue
                                                    if days < days:
                                                        if days <= 14:
                                                            continue
                                                        continue
                                                    '#ff9900'
                                                    continue
                                                7
                                                continue
                                if q_hash != '0':
                                    Analytics('NotActivated')
                                    a_resolut = False
                                    message += dop_message
                                    if mody.l0100l1l001l10011l0l0('lng') == 'RU':
                                        message += '<br><p align="center"><font color="#ffe3a4" size="12">\xd0\x92 \xd0\xbd\xd0\xb0\xd1\x81\xd1\x82\xd0\xbe\xd1\x8f\xd1\x89\xd0\xb5\xd0\xb5 \xd0\xb2\xd1\x80\xd0\xb5\xd0\xbc\xd1\x8f \xd0\xbf\xd1\x80\xd0\xbe\xd0\xb8\xd1\x81\xd1\x85\xd0\xbe\xd0\xb4\xd0\xb8\xd1\x82<br>\xd0\xb0\xd0\xba\xd1\x82\xd0\xb8\xd0\xb2\xd0\xb0\xd1\x86\xd0\xb8\xd1\x8f \xd0\xb2\xd0\xb0\xd1\x88\xd0\xb5\xd0\xb3\xd0\xbe ID<br>\xd0\x95\xd1\x81\xd0\xbb\xd0\xb8 \xd0\xbf\xd0\xbe \xd0\xb8\xd1\x81\xd1\x82\xd0\xb5\xd1\x87\xd0\xb5\xd0\xbd\xd0\xb8\xd1\x8e 3 \xd1\x87\xd0\xb0\xd1\x81\xd0\xbe\xd0\xb2 \xd0\xb0\xd0\xba\xd1\x82\xd0\xb8\xd0\xb2\xd0\xb0\xd1\x86\xd0\xb8\xd1\x8f \xd0\xbd\xd0\xb5 \xd0\xbf\xd1\x80\xd0\xbe\xd0\xb8\xd0\xb7\xd0\xbe\xd0\xb9\xd0\xb4\xd0\xb5\xd1\x82, \xd0\xbe\xd0\xb1\xd1\x80\xd0\xb0\xd1\x82\xd0\xb8\xd1\x82\xd0\xb5\xd1\x81\xd1\x8c \xd0\xb2 \xd0\xbf\xd0\xbe\xd0\xb4\xd0\xb4\xd0\xb5\xd1\x80\xd0\xb6\xd0\xba\xd1\x83 ' + MAIL + '</font><font color="#00ff00"><br>\xd0\xb8\xd0\xbb\xd0\xb8 \xd0\xbf\xd1\x80\xd0\xbe\xd0\xb4\xd0\xbb\xd0\xb8\xd1\x82\xd0\xb5 \xd1\x83\xd1\x81\xd0\xbb\xd1\x83\xd0\xb3\xd1\x83 \xd0\xbd\xd0\xb0 \xd1\x81\xd0\xb0\xd0\xb9\xd1\x82\xd0\xb5</font><br><a href="event:http://' + SITE_NAME + '/"><font color="#00d6b7"><B>www.WOTZJ.com</B></font></a></p>'
                                        if mody.IS_LOGIN:
                                            mody.IS_LOGIN = False
                                            SystemMessages.pushMessage(message, type = SystemMessages.SM_TYPE.Warning)
                                            continue
                                            message += '<br><p align="center"><font color="#ffe3a4" size="12">Now activate your ID<br>If activation does not complete after 3 hours, please contact support via email ' + MAIL + '</font><font color="#00ff00"><br>or prolong service on site</font><br><a href="event:http://' + SITE_NAME + '/"><font color="#00d6b7"><B>www.WOTZJ.com</B></font></a></p>'
                                            continue
                                            a_resolut = False
                                            if mody.l0100l1l001l10011l0l0('lng') == 'RU':
                                                message += '<p align="center"><font color="#ff3300">\xd0\x9e\xd0\xb7\xd0\xbd\xd0\xb0\xd0\xba\xd0\xbe\xd0\xbc\xd0\xb8\xd1\x82\xd0\xb5\xd0\xbb\xd1\x8c\xd0\xbd\xd1\x8b\xd0\xb9 \xd0\xbf\xd0\xb5\xd1\x80\xd0\xb8\xd0\xbe\xd0\xb4 \xd0\xb7\xd0\xb0\xd0\xb2\xd0\xb5\xd1\x80\xd1\x88\xd1\x91\xd0\xbd</font></p>'
                                                message += '<p align="center"><font color="#3b3825">' + a_date + '</font></p>'
                                                message += '<br><p align="center"><font color="#00ff00" size="12">\xd0\x92\xd1\x8b \xd0\xbc\xd0\xbe\xd0\xb6\xd0\xb5\xd1\x82\xd0\xb5 \xd0\xbf\xd1\x80\xd0\xb8\xd0\xbe\xd0\xb1\xd1\x80\xd0\xb5\xd1\x81\xd1\x82\xd0\xb8 \xd0\xbf\xd0\xbe\xd0\xbb\xd0\xbd\xd1\x83\xd1\x8e \xd0\xb2\xd0\xb5\xd1\x80\xd1\x81\xd0\xb8\xd1\x8e \xd1\x81\xd0\xb1\xd0\xbe\xd1\x80\xd0\xba\xd0\xb8</font></p>'
                                                message += '<p align="center"><a href="event:http://' + SITE_NAME + '"><font color="#00d6b7"><B>' + SITE_NAME + '</B></font></a></p>'
                                                if mody.IS_LOGIN:
                                                    mody.IS_LOGIN = False
                                                    SystemMessages.pushMessage(message, type = SystemMessages.SM_TYPE.Warning)
                                                    continue
                                                    message += '<p align="center"><font color="#ff3300">The trial period is completed</font></p>'
                                                    message += '<p align="center"><font color="#3b3825">' + a_date + '</font></p>'
                                                    message += '<br><p align="center"><font color="#00ff00" size="12">You can purchase the FULL version ModPack</font></p>'
                                                    message += '<p align="center"><a href="event:http://' + SITE_NAME + '"><font color="#00d6b7"><B>' + SITE_NAME + '</B></font></a></p>'
                                                    continue
                                                    message += '<p align="center"><font color="#ff3333">Server doesn`t respond!</font><br><font color="#ff9933" size="12">Temporarily granted the trial mode.<br>Please contact our support ' + MAIL + '</font></p>'
                                                    continue
                                                    if a_resolut and q_hash != '0':
                                                        Analytics('FistTrial')
                                                        if mody.l0100l1l001l10011l0l0('lng') == 'RU':
                                                            message += '<p align="center"><font color="#ff9933">\xd0\x94\xd0\xbe \xd0\xbf\xd0\xbe\xd0\xbb\xd0\xbd\xd0\xbe\xd0\xb9 \xd0\xb0\xd0\xba\xd1\x82\xd0\xb8\xd0\xb2\xd0\xb0\xd1\x86\xd0\xb8\xd0\xb8 \xd0\xb2\xd0\xb0\xd0\xbc \xd0\xbf\xd1\x80\xd0\xb5\xd0\xb4\xd0\xbe\xd1\x81\xd1\x82\xd0\xb0\xd0\xb2\xd0\xbb\xd0\xb5\xd0\xbd\xd0\xbe \xd0\xbd\xd0\xb5\xd1\x81\xd0\xba\xd0\xbe\xd0\xbb\xd1\x8c\xd0\xba\xd0\xbe \xd0\xb4\xd0\xbd\xd0\xb5\xd0\xb9 \xd0\xb4\xd0\xbb\xd1\x8f \xd0\xbe\xd0\xb7\xd0\xbd\xd0\xb0\xd0\xba\xd0\xbe\xd0\xbc\xd0\xbb\xd0\xb5\xd0\xbd\xd0\xb8\xd1\x8f</font></p>'
                                                            continue
                                                        message += '<p align="center"><font color="#ff9933">Before completing activation, you have few days for trial review</font></p>'
                                                        continue
                        if q_hash != '0' or mody.l0100l1l001l10011l0l0('lng') == 'RU':
                            message += '<p align="center"><font color="#ff9933">\xd0\x9e\xd0\xb7\xd0\xbd\xd0\xb0\xd0\xba\xd0\xbe\xd0\xbc\xd0\xb8\xd1\x82\xd0\xb5\xd0\xbb\xd1\x8c\xd0\xbd\xd1\x8b\xd0\xb9 \xd0\xbf\xd0\xb5\xd1\x80\xd0\xb8\xd0\xbe\xd0\xb4 \xd0\xb7\xd0\xb0\xd0\xb2\xd0\xb5\xd1\x80\xd1\x88\xd1\x91\xd0\xbd</font></p>'
                            continue
                        message += '<p align="center"><font color="#ff9933">The trial period is completed</font></p>'
                        continue
                    dop_message += '<p align="center"><font color="#ff9933">License detected</font></p>'
                    continue
                endDate = mody.CURRENT_DATE
                continue
            if Lic.hasLicense() or mody.l0100l1l001l10011l0l0('lng') == 'RU':
                dop_message += '<p align="center"><font color="#ff3333">\xd0\x9b\xd0\xb8\xd1\x86\xd0\xb5\xd0\xbd\xd0\xb7\xd0\xb8\xd1\x8f \xd0\xbf\xd1\x80\xd0\xbe\xd1\x81\xd1\x80\xd0\xbe\xd1\x87\xd0\xb5\xd0\xbd\xd0\xb0</font></p>'
                continue
            dop_message += '<p align="center"><font color="#ff3333">License has expired</font></p>'
            continue
        status = 'Error'
        continue
    (q_hash, a_resolut, a_date, a_version, a_stat) = mody.SERVER_RES
    continue
    '#00ff00'
    'days'
    '\xd0\xb4\xd0\xbd\xd1\x8f \xd0\xbe\xd1\x81\xd1\x82\xd0\xb0\xd0\xbb\xd0\xbe\xd1\x81\xd1\x8c'
    BigWorld.exit()
    continue

loop()
return None
(None, None, None, None, None, None, None, None, (None, None, None, None))
BigWorld.exit()
continue


# ================== TOP-LEVEL FUNCTIONS ==================