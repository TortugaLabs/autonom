#
# Perform http basic authentication
#
from bottle import route, request, response
from const import *
from ini import cfg
import base64
import userdb

AUTH_USER = 0
AUTH_PASSWD = 1

def authorize(basic_str):
  if not basic_str: return None, None

  auth = basic_str.split()
  if len(auth) != 2: return None, None
  if auth[0] != 'Basic':
    # We only support basic authentication
    return None, None
  auth = base64.b64decode(auth[1]).decode()
  auth = auth.split(':',1)
  if len(auth) != 2:
    # Unable to decode username password...
    return None, None

  pwck = cfg[CF_PWCK]
  user, ignore = userdb.check_password(auth[AUTH_USER], auth[AUTH_PASSWD],
                                      pwck, cfg)
  if user is None: return None, None

  grplst = userdb.get_groups(user,pwck,cfg)
  groups = ','.join(grplst)
  response.set_header('X-Username', user)
  response.set_header('X-Groups', groups)

  return user, grplst


@route('/basic-auth')
def auth():
  user, grplst = authorize(request.headers.get('Authorization'))
  if user:
    return 'Yes, go in.<br>User: {user}<br>Groups: {grps}'.format(
              user=user, grps=str(grplst))

  response.set_header('WWW-Authenticate',
                    'Basic realm="{realm}"'.format(
                      realm=cfg[CF_AUTH_REALM]
                    ))
  response.status = 401
  return 'Unauthenticated'
