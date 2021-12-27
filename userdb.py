from const import *

def get_backend(pwck,cfg):
  if pwck is None:
    for beid in cfg[CF_BACKENDS]:
      return cfg[CF_BACKENDS][beid]
  elif pwck in cfg[CF_BACKENDS]:
    return cfg[CF_BACKENDS][pwck]
  # This is an error
  return None

def check_password(user,passwd,pwck,cfg):
  backend = get_backend(pwck,cfg)
  return backend[CF_MODULE].check_password(user,passwd,backend,cfg)

def get_groups(user, pwck, cfg):
  backend = get_backend(pwck,cfg)
  return backend[CF_MODULE].get_groups(user,backend,cfg)

#
# Digest auth
#
import hashlib

def md5sum(x):
  return hashlib.md5(x.encode()).hexdigest()

def check_digest(method,req,pwck,cfg):
  # Read from backend:
  backend = get_backend(pwck,cfg)
  user, ha1 = backend[CF_MODULE].get_digest(req['username'],req['realm'],backend,cfg)
  if ha1 is None: return None, 'Login error'

  # Compute digest
  ha2 = md5sum('%s:%s' % (method, req['uri']))
  resp = md5sum('%s:%s:%s' % ( ha1, req['nonce'], ha2))

  # Check if it matches!
  if resp == req['response']:
    return user, None

  # ~ user = req['username']
  # ~ frealm = req['realm']
  # ~ ha1 = md5sum('%s:%s:%s' % (req['username'],req['realm'],req['username']))

  return None, 'Login error'

