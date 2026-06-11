# recovered via pycdc

t = time.localtime(time_utils._g_instance.serverUTCTime)
mody.CURRENT_DATE = datetime.date(t.tm_year, t.tm_mon, t.tm_mday)
serv_check = ServerCheck()
mody.fistStatus = STATUS
if STATUS.lower() != 'full':
    serv_check.run(STATUS)
    g_playerEvents.onAccountShowGUI -= onAccount
    return None
Lic = None(mody.CURRENT_DATE)
if Lic.status:
    data = Lic.getData()
    serv_check.run(Lic.status, data[1])
    continue
if mody.onLineActivated:
    serv_check.run()
    continue
