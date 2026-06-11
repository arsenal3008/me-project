# recovered via pycdc

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
