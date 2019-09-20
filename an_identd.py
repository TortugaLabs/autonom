#!/usr/bin/env python3
import sys
import os
import socket
import pwd


BIND_ADDR = '::'
IDENTD_PORT = 113
MAPFILE = 'map-file'
FAKEFILE = 'fake-file'
STRICT = 'strict-match'
cfg = {
  STRICT: False,
  MAPFILE: None,
  FAKEFILE: '.fakeid'
}


def drop_privileges(username):
  """ drop_privileges() -- setuid()/setgid() to something other than root.

  Args:
      username (str) - Username to attempt to setuid() to.

  Returns:
      Nothing.
  """
  if username is None:
    return
  # Check if this is even running as root in the first place
  if os.getuid() != 0:
    return

  uid = pwd.getpwnam(username).pw_uid
  gid = pwd.getpwnam(username).pw_gid

  # Always setgid() before setuid()
  os.setgroups([])
  os.setgid(gid)
  os.setuid(uid)

def is_valid_port(port):
  """ is_valid_port() -- Determines if a number is a valid value for a TCP/IP port.

  Args:
      port (int) - Port number.

  Returns:
      True if port is a valid port number.
      False if port is not a valid port number.
  """
  if port > 0 and port <= 65535:
    return True

  return False


def match_line(line, lport, rport):
  # ~ print('lport=%d rport=%d line=%s' % (lport,rport,line))
  try:
    line = line.split()
    port = int(line[1].split(':')[1],16)
    # ~ print('port=%d lport=%d' % (port,lport))
    if port != lport:
      return None
    port = int(line[2].split(':')[1],16)
    # ~ print('port=%d rport=%d' % (port,rport))
    if port != rport:
      return None
    # ~ print('state: %s' % line[3])
    if line[3] == '0A':
      return None
    return int(line[7])
  except IndexError:
    return None
  return None
  

def get_uid_from_port(source_ip, lport, rport):
  if cfg[STRICT]:
    if source_ip.startswith('::ffff:'):
      tables = ["/proc/net/tcp"]
    else:
      tables = ["/proc/net/tcp6"]
  else:
    tables = ["/proc/net/tcp6","/proc/net/tcp"]

  # ~ print('lport=%d rport=%d, tables=%s' % (lport, rport, tables))

  for target in tables:
    with open(target) as proc_net_tcp:
      for line in proc_net_tcp:
        uid = match_line(line, lport, rport)
        if not uid is None:
          return uid
  return None

def identd_response(srcip, data):
  import re

  if re.match(r"(\d+).*,.*(\d+)", data) is None:
    # Doesn't match "lport , lport" format
    return "%s : ERROR : INVALID-PORT" % data

  # Make sure ports are sane
  lport, rport = data.split(",")

  lport = int(re.sub(r"\D", "", lport))
  rport = int(re.sub(r"\D", "", rport))

  if not is_valid_port(lport) or not is_valid_port(rport):
    return "%s : ERROR : INVALID-PORT" % data

  uid = get_uid_from_port(srcip, lport, rport)
  if uid is None:
    return "%s : ERROR : NO-USER" % data

  try:
      username = pwd.getpwuid(uid).pw_name
  except KeyError:
      return "%s : ERROR : NO-USER" % data

  if cfg[MAPFILE]:
    try:
      with open(cfg[MAPFILE], "r") as fp:
        for line in fp:
          (key,val) = line.split(':')
          if val.strip() == username:
            return "%s : USERID : UNIX : %s" % (data, key.strip())
      return None
    except IOError as err:
      print('error reading mapfile: %s' % err)

  # See if user has a .fakeid
  fakeid = os.path.join(pwd.getpwuid(uid).pw_dir, cfg[FAKEFILE])
  if os.path.isfile(fakeid) and not os.path.islink(fakeid):
    try:
      with open(fakeid) as fake_id_file:
        for line in fake_id_file:
          # Skip comments
          if line[:1] == "#":
            continue

          # *nix username regex, but allow UPPERCASE as well because IRC
          if re.match(r"[a-zA-Z_][a-zA-Z0-9_-]*[$]?", line.rstrip()):
            username = line.rstrip()
            break
    except IOError as err:
      print('error reading fake id file: %s' % err)

  return "%s : USERID : UNIX : %s" % (data, username)

def main(user):
  try:
    sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
  except socket.error as message:
    sys.stderr.write("socket: %s\n" % message)
    sys.exit(os.EX_USAGE)

  sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  try:
    sock.bind((BIND_ADDR, IDENTD_PORT))
  except socket.error as message:
    sys.stderr.write("bind(%s,%d): %s\n" % (BIND_ADDR,IDENTD_PORT,message))
    sys.exit(os.EX_USAGE)

  try:
    sock.listen(5)
  except socket.error as message:
    sys.stderr.write("listen(5): %s\n" % message)
    sys.exit(os.EX_USAGE)

  drop_privileges(user)
  sys.stderr.write("Ready!\n")

  while True:
    client, addr = sock.accept()
    try:
      data = client.recv(1024).decode('ascii')
    #except socket.error as message:
    except:
      sys.stderr.write("receive error from %s: %s\n" % (addr[0], message))
      continue

    source_ip = addr[0]
    data = data.strip()
    sys.stderr.write("request from %s: %s\n" % (source_ip,data))
    response = identd_response(source_ip, data)
    sys.stderr.write("reply to %s: %s\n" % (source_ip, response))

    client.send("{}\r\n".format(response).encode('ascii'))
    client.close()


############################################################
# main
############################################################
if __name__ == "__main__":
  user='nobody'

  for opt in sys.argv[1:]:
    if opt.startswith('--user='):
      user = opt[7:]
    elif opt == '--no-user':
      user = None
    elif opt.startswith('--mapfile='):
      cfg[MAPFILE] = opt[10:]
    elif opt.startswith('--fakefile='):
      cfg[FAKEFILE] = opt[11:]
    elif opt == '--no-fakefile':
      cfg[FAKEFILE] = None
    elif opt == '--strict':
      cfg[STRICT] = True
      sys.stderr.write("Option %s is not implemented\n" % opt)
    elif opt == '--loose':
      cfg[STRICT] = False
    else:
      sys.stderr.write("Unknown option %s\n" % opt)
  
  main(user)







