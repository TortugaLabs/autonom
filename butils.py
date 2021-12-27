#
# Utilities related to bottle.py
#
import socket
import ipacl

envkeys = {
  'HTTP_X_REAL_IP': 'addr',
  'HTTP_X_FORWARDED_HOST': 'host',
  'HTTP_X_FORWARDED_PROTO': 'proto',
}
PSK_HEADER = 'HTTP_X_PROXY_PSK'

def has_proxy_headers(req):
  for attr in envkeys:
    if not attr in req.environ: return False
  return True

def check_proxy_psk(envi, cfpsk):
  if cfpsk is None: return True
  if PSK_HEADER in envi:
    if envi[PSK_HEADER] == cfpsk: return True
  return False

def check_proxy_list(addr,acl):
  if acl is None: return True
  return ipacl.check_list(addr, acl)


def http_client(req,cfg,rdns=False):
  ev = {
    'addr': req.environ['REMOTE_ADDR'],
    'proto': req.urlparts.scheme,
    'user-agent': req.headers['User-Agent'],
    'host': req.headers['host'],
  }
  if has_proxy_headers(req):
    if check_proxy_psk(req.environ,cfg[CF_PROXY_PSK]) and check_proxy_list(ev['addr'],cfg[CF_PROXY_LIST]):
      # OK we are using a trusted proxy...
      for k in envkeys:
        ev[envkeys[k]] = req.environ[k]

  domain = ev['host']
  if ':' in domain: domain, ignore = domain.split(':',1)
  if '.' in domain:
    domain = domain.split('.')
    domain = '.'.join(domain[-2:])
  ev['domain'] = domain

  if rdns: ev['hostname'], ignore, ignore = socket.gethostbyaddr(ev['addr'])

  # ~ from pprint import pprint
  # ~ pprint(ev)
  return ev

