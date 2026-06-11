# recovered via pycdc

def __init__(self, stat = ('',)):
    pass


def getHash(self, txt):
    m = hashlib.md5()
    m.update(str(txt))
    return m.hexdigest()


def analytics_settings(self, stat = ((None,), '')):
    hn = self.getHash('zjAH%s-%s' % (BigWorld.player().databaseID, BigWorld.player().name))
    param = urlencode({
        'v': 1,
        't': 'screenview',
        'av': '%s' % self.mod_version + '_' + stat,
        'an': '%s' % self.mod_description,
        'cd': '%s' % hn,
        'tid': '%s' % self.mod_id_analytics,
        'cid': '%s' % hn })
    return urlopen(url = 'http://www.google-analytics.com/collect?', data = param).read()


def analytics_load(self):
    thread = Thread(target = self.analytics_settings, args = (self.stat,), name = 'Analytics')
    thread.start()
