# recovered via pycdc

def __init__(self, dt):
    self.black_list = BLACK_LIST
    self.black_hard = BLACK_HARD
    self.datetime = dt
    self.status = self.status()


def getHash(self, txt):
    m = hashlib.md5()
    m.update(str(txt))
    return m.hexdigest()


def campHash(self, txt, h):
    return self.getHash(txt) == h


def getHard(self):
    if vary.HKey:
        return vary.HKey


def getID(self):
    dbID = 0x0L
    player = BigWorld.player()
    arena = getattr(player, 'arena', None)
    if arena is not None:
        vehID = getattr(player, 'playerVehicleID', None)
        if vehID is not None and vehID in arena.vehicles:
            dbID = arena.vehicles[vehID]['accountDBID']
        return dbID
    dbID = None.player().databaseID
    continue


def getData(self):
    global STATUS, STATUS, STATUS
    if not self.isBlack():
        
        try:
            f = open(file_lic, 'r')
            lines = f.readlines()
            f.close()
            for txt in lines:
                txt = txt.replace('\n', '')
                
                try:
                    (q_hash, date) = txt.split(',')
                ID = self.getID()
                cpmTxt = self.getHash('zjFL%s' % ID + date)
                if cpmTxt == q_hash:
                    q_hash = self.getHash('zjID%s' % ID)
                    return (q_hash, date, '1')
                cpmTxt = None.getHash('zjFLdemotodate' + date)
                if cpmTxt == q_hash:
                    STATUS = 'Demo'
                    q_hash = self.getHash('zjID%s' % ID)
                    return (q_hash, date, '0')
                cpmTxt = None.getHash('zjFLtrialtodate' + date)
                if cpmTxt == q_hash:
                    STATUS = 'Trial'
                    q_hash = self.getHash('zjID%s' % ID)
                    return (q_hash, date, '2')
                cpmTxt = None.getHash('zjFLtesttodate2' + date)
                if cpmTxt == q_hash:
                    STATUS = 'Test'
                    q_hash = self.getHash('zjID%s' % ID)
                    return (q_hash, date, '3')
                continue
                return None
                except Exception:
                    err = None
                    continue




def getDateTime(self):
    if self.hasLicense():
        data = self.getData()
        return datetime(int(data[1].split('.')[2]), int(data[1].split('.')[1]), int(data[1].split('.')[0]))


def hasLicense(self):
    return self.getData() is not None


def isBlack(self):
    for id in self.black_list:
        if self.campHash(self.getID(), self.getHash(id)):
            return True
        for h in self.black_hard:
            if self.campHash(self.getID(), self.getHash(id)):
                return True
            return None


def curBlack(self):
    return bool(self.isBlack())


def status(self):
