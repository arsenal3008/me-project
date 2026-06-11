# recovered via pycdc

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
