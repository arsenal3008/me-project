# recovered via pycdc

file_xml = mody.PATH_MODS + mody.FILE_xml
tick = 2

try:
    file_time = os.path.getmtime(file_xml)
    if time.time() - file_time < tick + 1:
        methodcaller('as_showGreenMessageS', '', APPLICATION + ' ' + mody.TEXT_MESSAGE_ConfLoad)(PlayerAvatar.selfMsg)
        mody.loadConf()
if mody.autoLoadConf:
    BigWorld.callback(tick, LoadConfLoop)

return None
continue
