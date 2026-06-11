# recovered via pycdc

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
