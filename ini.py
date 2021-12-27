#
# Handle ini file configuration
#
from const import *
import os.path
import srvio
import configparser
import sys
import login_form
import ticket, ipsess
import tlrealms, flatfiles
import ipacl

cfg = {
  CF_LISTEN:  '0.0.0.0',
  CF_PORT:    8080,
  CF_LOG:     LOG_SYSLOG,
  CF_LOG_EX:  APP_NAME,
  CF_PROVIDERS: {},
  CF_COOKIE_NAME: 'autonom_goo6Chah',
  CF_SESSION_SIG: 'uuChah2eigahthai5OeGhuz3Cieshahc',
  CF_TICKET_MAXAGE: 86400 * 365,
  CF_COOKIE_MAXAGE: 86400 * 10,
  CF_COOKIE_RENEW: 86400 * 7,
  CF_ATIME_MIN: 3600*4,
  CF_IPLOGIN_MAXAGE: 3600,
  CF_TEMPLATE_PATH: os.path.dirname(__file__) + '/views',
  CF_DOCROOT: os.path.dirname(__file__) + '/static',
  CF_TICKET_DB: 'autonom-tix.db',
  CF_FIXED_IP_LIST: None,
  CF_PROXY_LIST: None,
  CF_PROXY_PSK: None,
  CF_AUTH_REALM: None,
  CF_PWCK: None,
  RT_SESSION_MGR: {},
  CF_BACKENDS: {},
}

def return_false(c,k,v):
  return False


def copy_settings(src,dst,cfgparse=return_false,srcdesc='config section'):
  for key in src:
    if key in dst:
      if cfgparse(dst,key,src):
        continue
      elif isinstance(dst[key],int):
        dst[key] = src.getint(key)
      elif isinstance(dst[key],float):
        dst[key] = src.getfloat(key)
      elif isinstance(dst[key],bool):
        dst[key] = src.getboolean(key)
      elif isinstance(dst[key],str) or dst[key] is None:
        dst[key] = src[key]
      else:
        sys.stderr.write('Unconfigurable key {key} in {srcdesc}\n'.format(
                        key=key, srcdesc=srcdesc))
    else:
      sys.stderr.write('key {key} does not exist in {srcdesc}\n'.format(
                              key=key, srcdesc=srcdesc))

def cfg_main_parser(dst,key,src):
  if key == CF_LOG:
    # Handle log specification specially
    if src[key] is None:
      dst[CF_LOG] = LOG_STDIO
      dst[CF_LOG_EX] = None
    elif src[key].lower().startswith('file:'):
      dst[CF_LOG] = LOG_FILE
      dst[CF_LOG_EX] = src[key][5:]
    elif src[key].lower().startswith('syslog:'):
      dst[CF_LOG] = LOG_SYSLOG
      dst[CF_LOG_EX] = src[key][7:]
    elif src[key].lower() == 'syslog':
      dst[CF_LOG] = LOG_SYSLOG
      dst[CF_LOG_EX] = APP_NAME
    elif src[key].lower() == 'stdio':
      dst[CF_LOG] = LOG_STDIO
    elif src[key] != '':
      dst[CF_LOG] = LOG_FILE
      dst[CF_LOG_EX] = log
    else:
      dst[CF_LOG] = LOG_STDIO
      dst[CF_LOG_EX] = None
    return True
  return False


def cfg_init(args):
  if os.path.isfile(args.config):
    # If not daemon, switch default logging to stdio
    if not args.daemonize: cfg[CF_LOG] = LOG_STDIO

    #
    # Configure from file
    #
    ini = configparser.ConfigParser(allow_no_value=True)
    ini.read(args.config)
    copy_settings(ini[APP_NAME], cfg, cfg_main_parser, 'configuration file main section')

    for ss in ini:
      if ss == APP_NAME or ss == CF_DEFAULT: continue

      if CF_PROVIDER in ini[ss]:
        #
        # Configure a login provider
        #
        if ini[ss][CF_PROVIDER] == login_form.NAME:
          provider = login_form
        else:
          sys.stderr.write('Unknown provider {prov} in {sect}\n'.format(
                            prov=ini[ss][CF_PROVIDER], sect=ss))
          continue

        cfg[CF_PROVIDERS][ss] = provider.DEFAULTS

        cfg[CF_PROVIDERS][ss][CF_PROVIDER] = ini[ss][CF_PROVIDER]
        cfg[CF_PROVIDERS][ss][CF_ID] = ss
        cfg[CF_PROVIDERS][ss][CF_MODULE] = provider

        if hasattr(provider, 'cfgparse'):
          cfgparse = provider.cfgparse
        else:
          cfgparse = return_false

        copy_settings(ini[ss],cfg[CF_PROVIDERS][ss],cfgparse,'provider {sect}'.format(sect=ss))

        continue

      if CF_BACKEND in ini[ss]:
        #
        # Configure a password backend
        #
        if ini[ss][CF_BACKEND] == tlrealms.NAME:
          backend = tlrealms
        elif ini[ss][CF_BACKEND] == flatfiles.NAME:
          backend = flatfiles
        else:
          sys.stderr.write('Unknown backend {backend} in {sect}\n'.format(
                            backend=ini[ss][CF_BACKEND], sect=ss))
          continue

        cfg[CF_BACKENDS][ss] = backend.DEFAULTS

        cfg[CF_BACKENDS][ss][CF_BACKEND] = ini[ss][CF_BACKEND]
        cfg[CF_BACKENDS][ss][CF_ID] = ss
        cfg[CF_BACKENDS][ss][CF_MODULE] = backend

        if hasattr(backend, 'cfgparse'):
          cfgparse = backend.cfgparse
        else:
          cfgparse = return_false

        copy_settings(ini[ss],cfg[CF_BACKENDS][ss],cfgparse,'backend {sect}'.format(sect=ss))
        continue

      if ss in cfg:
        sys.stderr.write('Conflicting section name {sect} in {filename}\n'.format(
                          sect = ss,
                          filename = args.config))
        continue

      cfg[ss] = dict(ini[ss])

  if not args.cfv is None:
    #
    # Command line configuration
    #
    for cfv in args.cfv:
      if '=' in cfv:
        key, val = cfv.split('=',1)
      else:
        key  = cfv
        val = None
      if '.' in key:
        sect_name, key = cfv[0]
        if sect_name in cfg[CF_PROVIDERS]:
          sect = cfg[CF_PROVIDERS][sect_name]
        if sect_name in cfg[CF_BACKENDS]:
          sect = cfg[CF_BACKENDS][sect_name]
        elif sect_name in cfg:
          if not isinstance(cfg[sect_name],dict):
            sect = cfg[sect_name]
          else:
            sys.stderr.write('section {sect} in {cfv} is not allowed\n'.format(
                              sect=sect_name, cfv=cfv))
            continue
        else:
            sys.stderr.write('section {sect} in {cfv} does not exist\n'.format(
                              sect=sect_name, cfv=cfv))
            continue
      else:
        sect = cfg
      if not key in sect:
        sys.stderr.write('key {key} in {cfv} does not exist\n'.format(
                          key=key, cfv=cfv))
        continue

      if isinstance(sect[key],int):
        sect[key] = int(val)
      elif isinstance(sect[key],float):
        sect[key] = float(val)
      elif isinstance(sect[key],bool):
        # We do this to keep things consistent...
        tmp = configparser.ConfigParse()
        tmp[key] = { key: val }
        sect[key] = tmp[key].getboolean(key)
      elif isinstance(sect[key],str) or sect[key] is None:
        sect[key] = val
      else:
        sys.stderr.write('Unconfigurable key {key} in {cfv}\n'.format(
                          key=key, cfv=cfv))

  #
  # Initialize providers...
  #
  if len(cfg[CF_PROVIDERS]) == 0:
    sys.stderr.write('No login providers configured\n')
    sys.exit(1)
  for prid in cfg[CF_PROVIDERS]:
    module = cfg[CF_PROVIDERS][prid][CF_MODULE]
    module.cfg = cfg
    if hasattr(module,'init'): module.init(cfg[CF_PROVIDERS][prid])

  #
  # Initialize backends...
  #
  fails = []
  for beid in cfg[CF_BACKENDS]:
    module = cfg[CF_BACKENDS][beid][CF_MODULE]
    if not hasattr(module,'init'): continue
    if module.init(beid,cfg[CF_BACKENDS][beid],cfg): continue
    fails.append(beid)

  for beid in fails: del cfg[CF_BACKENDS][beid]

  if len(cfg[CF_BACKENDS]) == 0:
    sys.stderr.write('No backends configured\n')
    sys.exit(1)

  #
  # Command line arguments
  #
  if not args.listen is None: cfg[CF_LISTEN] = args.listen
  if not args.port is None: cfg[CF_PORT] = int(args.port)
  if not args.logger is None:
    cfg[CF_LOG] = args.logger
    if args.logger != LOG_STDIO: cfg[CF_LOG_EX] = args.logger_data

  #
  # Read the fixed-ip list
  #
  if not cfg[CF_FIXED_IP_LIST] is None:
    fixedips = {}
    with open(cfg[CF_FIXED_IP_LIST],'r') as fp:
      for line in fp:
        line = line.strip()
        if '#' in line: line = line.split('#',1)[0]
        line = line.split()
        if len(line) > 1:
          fixedips[line[0]] = line[1:]
    cfg[CF_FIXED_IP_LIST] = fixedips

  if not cfg[CF_PROXY_LIST] is None:
    cfg[CF_PROXY_LIST] = ipacl.parse_list(cfg[CF_PROXY_LIST])

  #
  # Load session mgrs
  #
  cfg[RT_SESSION_MGR]['ticket'] = ticket
  cfg[RT_SESSION_MGR]['ipsess'] = ipsess

  if args.daemonize:
    srvio.daemonize()
    if not args.pidfile is None:
      srvio.pidfile(args.pidfile)

  if cfg[CF_LOG] == LOG_SYSLOG:
    srvio.syslog_io(cfg[CF_LOG_EX])
  elif cfg[CF_LOG] == LOG_FILE:
    srvio.filelog_io(cfg[CF_LOG_EX])
  srvio.unbuffered_io()

  cfg[CF_TEMPLATE_PATH] = cfg[CF_TEMPLATE_PATH].split(':')


