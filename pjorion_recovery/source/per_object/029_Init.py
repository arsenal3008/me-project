# recovered via pycdc

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
