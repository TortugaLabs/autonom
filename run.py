#/usr/bin/env python -u
import sys
import os

def io_syslog(fh,tag):
  r,w = os.pipe()
  cpid = os.fork()
  if cpid == 0:
    # Child...
    os.close(w)
    sys.stdin.close()
    sys.stdout.close()
    sys.stderr.close()
    fin = os.fdopen(r)

    # ~ x = open('log-%s.txt' % tag,'w')
    import syslog
    
    for line in fin:
      line = line.rstrip()
      if not line: continue
      syslog.syslog("%s: %s" % (tag,line))
      # ~ x.write("%s: %s\n" % (tag,line))
      # ~ x.flush()
    sys.exit(0)

  os.close(r)
  os.dup2(w, fh.fileno())
  os.close(w)

import autonom
import login_form
import ident_sso
import gauth

proxy_list = {
   '172.17.1.1': True
 }

autonom.register_provider(login_form.new_provider({
  login_form.PASSWDFILE: os.getenv('HTPASSWD'),
  autonom.GROUPSFILE: os.getenv('HTGROUPS')
}))
autonom.register_provider(ident_sso.new_provider({
  autonom.GROUPSFILE: os.getenv('HTGROUPS'),
  ident_sso.MAPFILE: os.getenv('IDENT_SSO_MAP'),
  ident_sso.ACL: os.getenv('IDENT_SSO_ACL').split(),
  ident_sso.PROXY_LIST: proxy_list,
  ident_sso.SERVERPORTMAP: { 9443: 443 }
}))
autonom.register_provider(gauth.new_provider({
  autonom.GROUPSFILE: os.getenv('HTGROUPS'),
  gauth.CLIENT_ID: os.getenv('CLIENT_ID'),
  gauth.CLIENT_SECRET: os.getenv('CLIENT_SECRET'),
  gauth.MAP_FILE: os.getenv('GAUTH_MAP')
}))


MAPTABLE = 'map'
PROXIES = 'proxy-list'
GRPTAB = 'group-table'

ipaddr_cfg = {
  MAPTABLE: {
    # '172.18.4.119': 'homeuser',
    '172.18.4.178': 'iptv'
  },
  PROXIES: proxy_list,
  GRPTAB: {},
  autonom.GROUPSFILE: os.getenv('HTGROUPS')
}

def ipaddr_sso():
  from bottle import request, response

  remote_ip = request.environ.get('REMOTE_ADDR')
  if remote_ip in ipaddr_cfg[PROXIES]:
    hdrs = dict(request.headers)
    if 'X-Real-Ip' in hdrs:
      remote_ip = hdrs['X-Real-Ip']

  print('remote ip: %s' %remote_ip)
  if not remote_ip in ipaddr_cfg[MAPTABLE]:
    return None

  remote_user = ipaddr_cfg[MAPTABLE][remote_ip]
  if not remote_user in ipaddr_cfg[GRPTAB]:
    ipaddr_cfg[GRPTAB][remote_user] = autonom.get_groups(remote_user, ipaddr_cfg)  
  grps = ipaddr_cfg[GRPTAB][remote_user]

  response.set_header('X-Username', remote_user)
  response.set_header('X-Groups', grps)
  return "Active Session: %s\nGroups: %s\n" % (remote_user,grps)

autonom.setcfg(autonom.AUTH_HOOK,ipaddr_sso)


from bottle import route, request
@route('/hello')
def show_headers():
  env = dict(request.environ)
  import pprint
  return '''
      <pre>
	URL: %s

	%s
      </pre>
  ''' % (request.url, pprint.pformat( env ))

############################################################
# main
############################################################
if __name__ == "__main__":
  listen='0.0.0.0'
  port=8080

  for opt in sys.argv[1:]:
    if opt.startswith('--listen='):
      listen = opt[9:]
    elif opt.startswith('--port='):
      port = int(opt[7:])
    elif opt.startswith('--pid='):
      with open(opt[6:],'w') as fh:
       fh.write("%d\n" % os.getpid())
    elif opt.startswith('--syslog='):
      io_syslog(sys.stdout,'%s(out)' % opt[9:])
      io_syslog(sys.stderr,'%s(err)' % opt[9:])
    elif opt == '--detach' or opt == '-d':
      res = os.fork()
      if res > 0:
       # Running on parent...
       sys.exit(0)
       os.setsid()
      print("Running as %d" % os.getpid())
    else:
      sys.stderr.write("Unknown option %s\n" % opt)
  
  autonom.run(host=listen, port=port)







