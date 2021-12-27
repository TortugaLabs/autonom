#
# Manage auth tickets
#
import shelve
from const import *
import srvio
import uuid
from time import time
import bottle
import butils

TX_CREATED = 0
TX_USER = 1
TX_ADDR = 2
TX_HOST = 3
TX_USERAGENT = 4
TX_COOKIE_CREATED = 5
TX_LAST_SEEN = 6
TX_PROVIDER = 7
TX_COLS = 8

COL_NAMES = [
  'Ticket Age',
  'ID',
  'Address',
  'Host',
  'User-Agent',
  'Cookie Age',
  'Last Seen',
  'Provider',
]

def get_provider(sdat):
  return sdat[TX_PROVIDER]

def new_cookie(tixdat,cfg):
  client = butils.http_client(bottle.request,cfg,True)

  with shelve.open(cfg[CF_TICKET_DB]) as db:
    while True:
      tixid = str(uuid.uuid4())
      if not tixid in db: break

    now = time()

    tixdat[TX_ADDR] = client['addr']
    tixdat[TX_HOST] = client['hostname']
    tixdat[TX_USERAGENT] = client['user-agent']
    tixdat[TX_COOKIE_CREATED] = now
    tixdat[TX_LAST_SEEN] = now

    from pprint import pprint
    pprint(tixdat)

    db[tixid] = tixdat

  if client['proto'] == 'https':
    secure=True
  else:
    secure=False

  bottle.response.set_cookie(cfg[CF_COOKIE_NAME],tixid,
                            secret=cfg[CF_SESSION_SIG],
                            max_age=cfg[CF_COOKIE_MAXAGE],
                            domain=client['domain'],
                            path='/',
                            secure=secure,
                            httponly=True)
  return tixid


def get_session(cfg):
  tixid = bottle.request.get_cookie(cfg[CF_COOKIE_NAME],
                                    secret=cfg[CF_SESSION_SIG])
  if not tixid: return None,None

  expire_tickets(cfg)
  now = time()

  with shelve.open(cfg[CF_TICKET_DB]) as db:
    if not tixid in db: return None,None

    tixdat = db[tixid]
    if now - tixdat[TX_COOKIE_CREATED] > cfg[CF_COOKIE_RENEW]:
      # Time to re-new cookie
      del db[tixid]
      tixid = None
    elif now - tixdat[TX_LAST_SEEN] > cfg[CF_ATIME_MIN]:
      # Just update last seen
      tixdat[TX_LAST_SEEN] = now
      db[tixid] = tixdat

  # We have a valid ticket...
  if tixid is None:
    # But we need to re-issue cookie
    tixid = new_cookie(tixdat,cfg)
    srvio.ts_print('Re-baked cookie:{id} for {user}'.format(user=tixdat[TX_USER],id=tixid))

  # Return the user data
  return tixdat[TX_USER], tixdat


def new_session(user, prid, cfg):
  expire_tickets(cfg)

  tixdat = [None]*TX_COLS
  tixdat[TX_CREATED] = time()
  tixdat[TX_USER] = user
  tixdat[TX_PROVIDER] = prid

  tixid = new_cookie(tixdat,cfg)

  srvio.ts_print('Issued a new ticket:{id} for {user}'.format(user=user,id=tixid))
  return tixid

def expire_tickets(cfg):
  ticket_maxage = cfg[CF_TICKET_MAXAGE]
  cookie_maxage = cfg[CF_COOKIE_MAXAGE]

  expired = []
  now = time()

  with shelve.open(cfg[CF_TICKET_DB]) as db:
    for tixid in db:
      tixdat = db[tixid]
      if tixdat[TX_CREATED]+ticket_maxage < now:
        expired.append(tixid)
        continue
      if tixdat[TX_COOKIE_CREATED]+cookie_maxage < now:
        expired.append(tixid)
        continue

    for tixid in expired:
      tixdat = db[tixid]
      del db[tixid]
      srvio.ts_print('Expired {sid}(user={user})'.format(
                      sid=tixid,
                      user=tixid[TX_USER],
                    ))


def del_session(cfg):
  tixid = bottle.request.get_cookie(cfg[CF_COOKIE_NAME],
                                    secret=cfg[CF_SESSION_SIG])
  if not tixid: return
  expire_tickets(cfg)

  with shelve.open(cfg[CF_TICKET_DB]) as db:
    if tixid in db: del db[tixid]

def user_sessions(user,cfg):
  expire_tickets(cfg)
  ret = []
  with shelve.open(cfg[CF_TICKET_DB]) as db:
    for tixid in db:
      tixdat = list(db[tixid])
      if tixdat[TX_USER] == user:
        tixdat[TX_USER] = tixid
        ret.append(tixdat)
  return ret



