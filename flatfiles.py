#/usr/bin/env python
from const import *
import sys
import mkpasswd
import crypt

NAME = 'flatfiles'
DEFAULTS = {
  CF_PWTYPE: FF_DEFAULT,
  CF_PASSWD: None,
  CF_GROUPS: None,
  CF_DIGEST: None,
}

# ~ def cfgparse(dst,key,src):
  # ~ return False

def init(beid,cfv,cfg):
  ret = True
  cfv[CF_PWTYPE] = cfv[CF_PWTYPE].lower()
  if not cfv[CF_PWTYPE] in (FF_APACHE2, FF_UNIX):
    sys.stderr.write('Unknown password style in backend {beid}\n'.format(
                      beid=beid))
    ret = False
  if cfv[CF_PASSWD] is None:
    sys.stderr.write('Password file not configure in backend {beid}\n'.format(
                      beid=beid))
    ret = False
  if cfv[CF_GROUPS] is None:
    sys.stderr.write('Warnning: groups not configure in backend {beid}\n'.format(
                      beid=beid))
  return ret

def check_password(user,passwd,cfv,cfg):
  user = user.lower()
  with open(cfv[CF_PASSWD],'r') as fp:
    for line in fp:
      line = line.strip().split(':',2)
      if len(line) < 2: continue
      if line[0] != user: continue
      if line[1].startswith('$apr1$'):
        inp = mkpasswd.apr1_crypt(line[1],passwd)
        if inp == line[1]:
          return line[0], None
      else:
        inp = crypt.crypt(passwd, line[1])
        if inp == line[1]:
          return line[0], None

  return None, 'Login failed'

def get_groups(user,cfv,cfg):
  if cfv[CF_GROUPS] is None: return []

  grps = []
  user = user.lower()
  with open(cfv[CF_GROUPS],'r') as fp:
    for line in fp:
      line = line.strip().split(':')
      if len(line) == 2:
        # This is a htgroup file (https://httpd.apache.org/docs/2.4/mod/mod_authz_groupfile.html)
        if user in line[1].split():
          grps.append(line[0])
      elif len(line) >= 4:
        if user in line[1].split(','):
          grps.append(line[0])
  return grps

def get_digest(user,realm,cfv,cfg):
  if cfv[CF_DIGEST] is None: return None,'digest file not configured'
  user = user.lower()

  with open(cfv[CF_DIGEST],'r') as fp:
    for line in fp:
      line = line.strip().split(':')
      if len(line) != 3: continue
      if line[0] == user and line[1] == realm:
        return line[0], line[2]

  return None, 'No match found!'
