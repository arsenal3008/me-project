# recovered via pycdc

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
    dbID = None.player().databaseID
    continue


def query(self):
    ID = self.getID()
    k = random.randint(10000, 100000000)
    q_hash = self.getHash('ZJ1WIN%s' % ID)
    param = urlencode({
        'q': q_hash,
        'ver': '%s' % BUILD,
        'trial': '%s' % k })
    url_list = [
        'i.zjmods.ru',
        'z.zjmods.ru',
        'i.zjshaitan.ru',
        'i.wotzj.com',
        'z.zjshaitan.ru',
        'i.wotwin.ru',
        'i.greenwot.ru',
        'z.greenwot.ru']
    
    def serv_query(serv_url):
