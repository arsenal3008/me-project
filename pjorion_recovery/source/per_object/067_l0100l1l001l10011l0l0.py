# recovered via pycdc

getFullClientVersion = getFullClientVersion
import helpers
AUTH_REALM = AUTH_REALM
import constants
vClient = getFullClientVersion().split('v.')[1].split(' ')[0]
vClientInt = int(vClient.split('.')[0]) * 10000 + int(vClient.split('.')[1]) * 100 + int(vClient.split('.')[2]) * 1
if type == 'cmp' and curVer is not None:
    return vClientInt <= int(curVer.split('.')[0]) * 10000 + int(curVer.split('.')[1]) * 100 + int(curVer.split('.')[2]) * 1
if None == 'lng':
    return AUTH_REALM
if None == 'str':
    return vClient
if None == 'int':
    return vClientInt
