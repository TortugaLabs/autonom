#
# Manage auth tickets
#
from const import *
import srvio
import uuid
from time import time
import bottle
import butils

IS_CREATED = 0
IS_USER = 1
IS_ADDR = 2
IS_LAST_SEEN = 3
IS_PROVIDER = 4
IS_COLS = 5

COL_NAMES = [
  'Ticket Age',
  'User',
  'Address',
  'Last Seen',
  'Provider',
]

session_db = {}

def get_provider(sdat):
  return sdat[IS_PROVIDER]

def new_session(user,prid,cfg):
  expire_ips(cfg)
  client = butils.http_client(bottle.request,cfg)
  sid = client['addr']
  now = time()

  sdat = [None]*IS_COLS
  sdat[IS_CREATED] = now
  sdat[IS_USER] = user
  sdat[IS_ADDR] = sid
  sdat[IS_LAST_SEEN] = now
  sdat[IS_PROVIDER] = prid

  session_db[sid] = sdat

  srvio.ts_print('New IP session:{sid} for {user}'.format(user=user,sid=sid))
  return sid

def get_session(cfg):
  client = butils.http_client(bottle.request,cfg)
  sid = client['addr']
  now = time()

  expire_ips(cfg)

  if not sid in session_db: return None, None

  sdat = session_db[sid]
  return sdat[IS_USER], sdat

def expire_ips(cfg):
  ip_maxage = cfg[CF_IPLOGIN_MAXAGE]
  expired = []
  now = time()

  for sid in session_db:
    if session_db[sid][IS_LAST_SEEN] + ip_maxage < now:
      expired.append(sid)
  for sid in expired:
    srvio.ts_print('Expire {sid}(user={user})'.format(
                    sid=sid, user=session_db[sid][IS_USER]
                  ))
    del session_db[sid]

def del_session(cfg):
  client = butils.http_client(bottle.request,cfg)
  sid = client['addr']
  expire_ips(cfg)

  if sid in session_db: del session_db[sid]

def user_sessions(user,cfg):
  expire_ips(cfg)
  ret = []
  for sid in session_db:
    if session_db[sid][IS_USER] != user: continue
    ret.append(list(session_db[sid]))
  return ret
