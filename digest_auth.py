#/usr/bin/env python
#
# Perform http digest authentication
#
from bottle import route, request, response
from const import *
from ini import cfg

import userdb
import random
import shlex


def gen_noise(len = 16):
  letters = '0123456789abcdef'
  salt = ''
  for x in range(len):
    salt = salt + random.choice(letters)
  return salt

@route('/digest-auth')
def auth():
  user, grps = authorize(request.headers.get('Authorization'))
  if user:
    return 'Yes, go in Mr {name}.  {grps}'.format(name=user,grps=grps)

  nonce = gen_noise(32)
  opaque = gen_noise(32)

  #print("nonce=%s\nopaque=%s\n" % (nonce, opaque))
  response.set_header('WWW-Authenticate', 'Digest realm="{realm}", nonce="{nonce}", opaque="{opaque}"'.format(
              realm=cfg[CF_AUTH_REALM], nonce=nonce, opaque=opaque))
  response.status = 401
  return 'Unauthenticated'


def authorize(auth):
  if not auth: return None, None
  auth = shlex.split(auth)
  print(auth)
  if len(auth) < 2 or auth[0] != 'Digest': return None, None

  req = {}
  for x in auth:
    if x[-1:] == ',':
      x = x[:-1]
    x = x.split('=',2)
    if len(x) == 0:
      continue
    elif len(x) == 1:
      req[x[0].lower()] = True
    else:
      req[x[0].lower()] = x[1]

  # make sure that all fields are there...
  for x in ['username','realm','nonce','uri','response']:
    if not x in req:
      print('Missing "%s" in response' % x)
      return None, None

  method = request.headers.get('X-Origin-Method')
  if not method: method = 'GET'
  print('method: {}'.format(method))

  pwck = cfg[CF_PWCK]
  user, ignore = userdb.check_digest(method,req,pwck,cfg)
  if user is None: return None,None

  grplst = userdb.get_groups(user,pwck,cfg)
  groups = ','.join(grplst)

  response.set_header('X-Username', user)
  response.set_header('X-Groups', groups)

  return user,grplst
