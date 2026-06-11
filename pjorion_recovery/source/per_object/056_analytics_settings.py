# recovered via pycdc

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
