#/usr/bin/env python
from const import *
from ini import cfg, cfg_init
import argparse
import bottle
import webapi
import basic_auth
import digest_auth

############################################################
# main
############################################################
if __name__ == "__main__":
  class LogParseAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
      if option_string == '--syslog'  or option_string == '-S':
        namespace.logger = LOG_SYSLOG
        setattr(namespace, 'logger_data', values)
      elif option_string == '--logfile' or option_string == '-L':
        namespace.logger = LOG_FILE
        setattr(namespace, 'logger_data', values[0])

  cli = argparse.ArgumentParser(prog = APP_NAME,
                                description = 'Authentication master')
  cli.add_argument('-c','--config', help='Configuration file',
                    action='store', default = DEFAULT_CONFIG_FILE)
  cli.add_argument('-C','--cfv', help='Set config item', action='append')

  cli.add_argument('-l', '--listen', help='Listen on address')
  cli.add_argument('-p', '--port', help='Bind to port')

  cli.add_argument('-d', '--daemon', help='Send process to background',
                    action='store_true', dest='daemonize')
  cli.add_argument('-P', '--pidfile', help='Save PID to file')

  cli.add_argument('-S', '--syslog', help='Log to syslog',
                    action=LogParseAction, nargs='?',  dest='logger')
  cli.add_argument('-e', '--stdio', help='Log to stdio',
                    action='store_const', const=LOG_STDIO, dest='logger')
  cli.add_argument('-L', '--logfile', help='Log to file',
                    action=LogParseAction, nargs=1, dest='logger')
  cli.set_defaults(logger=None)

  cli.add_argument('-D', '--debug', help='Enable debugging', action='store_true')

  args = cli.parse_args()
  if args.debug: bottle.debug()
  if bottle.DEBUG: print(args)

  cfg_init(args)
  bottle.TEMPLATE_PATH = cfg[CF_TEMPLATE_PATH]

  if bottle.DEBUG:
    from pprint import pprint
    pprint(cfg)
  bottle.run(host=cfg[CF_LISTEN],port=cfg[CF_PORT])




