# recovered via pycdc

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
