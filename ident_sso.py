#/usr/bin/env python
from bottle import route, request, response, abort, template
import sys
import autonom
import fnmatch

MAPFILE = 'mapfile'
ACL = 'access-list'
GROUPSFILE = autonom.GROUPSFILE
IDENT_PORT = 'ident-port'
SERVERPORTMAP = 'server-port-map'

def check_acl(ip, acl):
  for m in acl:
    if fnmatch.fnmatch(ip, m):
      return True
  return False

def ident_query(rem_ip, rem_port, my_port,port=113):
  try:
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((rem_ip, port))
    s.sendall('%d, %d' % (rem_port, my_port))
    data = s.recv(1024)
    s.close()
    resp = data.strip().split(':',4)
    if len(resp) != 4 or resp[1].strip() != 'USERID' or resp[2].strip() != 'UNIX':
      return None

    return resp[3].strip()
  except IOError as err:
    sys.stderr.write("remote query failed\n")
  return None

def map_user(raw_user, mapfile):
  try:
    with open(mapfile, "r") as fp:
      for line in fp:
       (key,val) = line.split(':')
       if key.strip() == raw_user:
        return val.strip()
  except IOError as err:
    sys.stderr.write("Error reading %s" % mapfile)
  return None

def auto_login_hook(pid):
  cfg = autonom.get_provider(pid)
  hdrs = dict(request.headers)

  if 'X-My-Real-Ip' in hdrs and 'X-My-Real-Port' in hdrs and 'X-My-Server-Port' in hdrs:
    remote_ip = hdrs['X-My-Real-Ip']
    remote_port = int(hdrs['X-My-Real-Port'])
    server_port = int(hdrs['X-My-Server-Port'])
    if SERVERPORTMAP in cfg:
      if server_port in cfg[SERVERPORTMAP]:
       server_port = cfg[SERVERPORTMAP][server_port]
  else:
    return None

  if ACL in cfg:
    if not check_acl(remote_ip,cfg[ACL]):
     return None

  remote_user = ident_query(remote_ip, remote_port, server_port, cfg[IDENT_PORT])
  if not remote_user:
    return None

  if MAPFILE in cfg:
    remote_user = map_user(remote_user, cfg[MAPFILE])
    if not remote_user:
      return None

  grps = autonom.get_groups(remote_user,cfg)
  if 'url' in request.query:
    url = request.query['url']
  else:
    url = ''

  return autonom.new_session(remote_user,grps,url)

def new_provider(opts):
  cfg = {
    IDENT_PORT: 113,
    autonom.PRE_LOGIN_HOOK: auto_login_hook
  }
  for optkey in [GROUPSFILE, MAPFILE, ACL, IDENT_PORT, SERVERPORTMAP]:
    if optkey in opts:
      cfg[optkey] = opts[optkey]

  return cfg

