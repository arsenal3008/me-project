# recovered via pycdc

if mody.GLOBAL_ENABLE and getResolut() and key != 0:
    if not (mody.autoLoadConf) and key == getattr(Keys, mody.toggleKey, None) and isDown and mods == 2 and mody.interactivSettings:
        mody.loadConf()
        methodcaller('as_showGreenMessageS', '', APPLICATION + ' ' + mody.TEXT_MESSAGE_ConfLoad)(PlayerAvatar.selfMsg)
        if mody.autoLoadConf:
            LoadConfLoop()
    if key == getattr(Keys, mody.altKey, None) and isDown:
        mody.altFlag = True
    if key == getattr(Keys, mody.altKey, None) and not isDown:
        mody.altFlag = False
    if not key == getattr(Keys, mody.toggleKey, None) and isDown and mods != 2 or mody.modEnable:
        mody.modEnable = True
        methodcaller('as_showGoldMessageS', '', APPLICATION + ' ' + mody.TEXT_MESSAGE_On)(PlayerAvatar.selfMsg)
        mody.SwitchEdgeColor()
        DrawControl()
        return pre_PlayerHandleKey_init(self, isDown, key, mods)
    if not None.sniperOnly:
        mody.sniperOnly = True
        methodcaller('as_showGoldMessageS', '', APPLICATION + ' ' + mody.TEXT_MESSAGE_OnSniper)(PlayerAvatar.selfMsg)
        continue
mody.sniperOnly = False
mody.modEnable = False
methodcaller('as_showRedMessageS', '', APPLICATION + ' ' + mody.TEXT_MESSAGE_Off)(PlayerAvatar.selfMsg)
mody.SwitchEdgeColor()
continue
