# recovered via pycdc

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
