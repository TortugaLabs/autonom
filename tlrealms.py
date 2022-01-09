#/usr/bin/env python
from const import *
import os.path
import sys
import mkpasswd
import crypt
import glob

NAME = 'tlrealms'
DEFAULTS = {
  CF_TLREALMS_DATA: None,
}

USER_PWD = '{path}/users.d/{user}.pwd'
GROUPS_PATTERN = '{path}/groups.d/*.cfg'

# ~ def cfgparse(dst,key,src):
  # ~ return False


def init(beid,cfv,cfg):
  if cfv[CF_TLREALMS_DATA] is None:
    sys.stderr.write('{key} not configured in backend {beid}\n'.format(
                      key=CF_TLREALMS_DATA,beid=beid))
    return False
  if not os.path.isdir(cfv[CF_TLREALMS_DATA]):
    sys.stderr.write('{dir} for configured {key} not found in backend {beid}\n'.format(
                      dir=cfv[CF_TLREALMS_DATA],key=CF_TLREALMS_DATA,beid=beid))
    return False
  return True

def check_password(user,passwd,cfv,cfg):
  user = user.lower()
  if not os.path.isfile(USER_PWD.format(path=cfv[CF_TLREALMS_DATA],user=user)):
    return None, 'User {user} does not exist'.format(user=user)
  with open(USER_PWD.format(path=cfv[CF_TLREALMS_DATA],user=user),'r') as fp:
    for line in fp:
      line = line.strip().split(maxsplit=1)
      if line == 1: continue
      if line[0] == 'unix':
        inp = crypt.crypt(passwd, line[1])
        if inp == line[1]: return user, None
      elif line[0] == 'htpasswd':
        inp = mkpasswd.apr1_crypt(line[1],passwd)
        if inp == line[1]: return user, None
  return None, 'Wrong password'

def get_groups(user,cfv,cfg):
  user = user.lower()
  grps = []

  for grpfile in glob.glob(GROUPS_PATTERN.format(path=cfv[CF_TLREALMS_DATA])):
    with open(grpfile,'r') as fp:
      for line in fp:
        line = line.strip().split()
        if len(line) < 2: continue
        if line[0] != 'mem': continue
        line = line[1:]
        if user in line:
          grps.append(grpfile.split('/')[-1][:-4])
          break
  return grps

def get_digest(user,realm,cfv,cfg):
  user = user.lower()
  if not os.path.isfile(USER_PWD.format(path=cfv[CF_TLREALMS_DATA],user=user)):
    return None, 'User {user} does not exist'.format(user=user)
  with open(USER_PWD.format(path=cfv[CF_TLREALMS_DATA],user=user),'r') as fp:
    for line in fp:
      line = line.strip().split(maxsplit=1)
      if line == 1: continue
      if line[0] == 'htdigest':
        digest = line[1].split(':',1)
        if len(digest) == 2:
          if digest[0] == realm:
            return user, digest[1]
  return None, 'password not found'
