# recovered via pycdc

if actionName.lower().find('http://') or actionName.lower().find('https://') is None:
    return old_NotificationsActionsHandlers_handleAction(self, model, typeID, entityID, actionName)
if None not in modules:
    g_eventBus.handleEvent(OpenLinkEvent(OpenLinkEvent.SPECIFIED, actionName))
