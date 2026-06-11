# recovered via pycdc

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
