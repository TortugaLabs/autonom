#/usr/bin/env python
#
# User interface
#
from bottle import route, static_file, template, request, redirect, response, abort
from ini import cfg
from const import *
from urllib.parse import quote_plus as urlquote
from time import time
import butils
import userdb
import os

@route('/')
def index():
  redirect('/hello')

@route('/static/<filename:path>')
def serve_static(filename):
  return static_file(filename, root=cfg[CF_DOCROOT])

@route('/favicon.ico')
def favicon():
  return static_file('favicon.ico', root=cfg[CF_DOCROOT])

@route('/hello')
@route('/hello/<smgr>/<name>')
@route('/hello/<smgr>')
def hello_world(smgr=DEFAULT_SESSMGR,name='stranger'):
  if not smgr in cfg[RT_SESSION_MGR]:
    return abort(404,'Missing session manager {smgr}'.format(smgr=smgr))
  smod = cfg[RT_SESSION_MGR][smgr]
  sess,ticket =  smod.get_session(cfg)
  if sess is None:
    prid = None
    cfv = None
    grplst = None
  else:
    prid = smod.get_provider(ticket)
    cfv = cfg[CF_PROVIDERS][prid]
    grplst = userdb.get_groups(sess,cfv[CF_PWCK],cfg)

  kw = {
    'smgr': smgr,
    'name': name,
    'session': sess,
    'ticket':  ticket,
    'groups': grplst,
    'method': request.method,
    'path_info': request.path,
    'url_args': request.url_args,
    'url': request.url,
    'urlparts': request.urlparts,
    'remote_addr': request.environ['REMOTE_ADDR'],
    'remote_route': request.remote_route,
    'headers': request.headers,
    'cookies': request.cookies,
    'query': request.query,
    'query_string': request.query_string,
    'forms': request.forms,
    'env': request.environ,
  }
  return template('hello',**kw)

@route('/login')
@route('/login/<smgr>')
def web_login(smgr=DEFAULT_SESSMGR):
  if not smgr in cfg[RT_SESSION_MGR]:
    return abort(404,'Missing session manager {smgr}'.format(smgr=smgr))
  smod = cfg[RT_SESSION_MGR][smgr]

  user,tix = smod.get_session(cfg)
  if user:
    prid = smod.get_provider(tix)
    cfv = cfg[CF_PROVIDERS][prid]
    grplst = userdb.get_groups(user,cfv[CF_PWCK],cfg)
    ret = {
      'active': True,
      'user': user,
      'ticket': tix,
      'groups': grplst,
    }
  else:
    ret = {
      'active': False,
      'providers': [],
      'url': None,
    }
    if 'url' in request.params: ret['url'] = request.params['url']
    if ret['url'] is None:
      suffix = ''
    else:
      suffix = '?url=' + urlquote(ret['url'])

    for p in cfg[CF_PROVIDERS]:
      ret['providers'].append({
        'href': cfg[CF_PROVIDERS][p][CF_HREF].format(
                                id=p, suffix=suffix,smgr=smgr),
        'desc': cfg[CF_PROVIDERS][p][CF_DESC],
      })

  return template('login-menu',**ret)

@route('/logout/confirm')
@route('/logout/confirm/<smgr>')
def do_logout(smgr=DEFAULT_SESSMGR):
  if not smgr in cfg[RT_SESSION_MGR]:
    return abort(404,'Missing session manager {smgr}'.format(smgr=smgr))
  smod = cfg[RT_SESSION_MGR][smgr]

  user, tix = smod.get_session(cfg)
  if user:
    smod.del_session(cfg)

  if 'url' in request.params:
    url = request.params['url']
  else:
    url = '/login/{smgr}'.format(smgr=smgr)
  redirect(url)

@route('/logout')
@route('/logout/menu')
@route('/logout/menu/<smgr>')
def web_logout(smgr=DEFAULT_SESSMGR):
  if not smgr in cfg[RT_SESSION_MGR]:
    return abort(404,'Missing session manager {smgr}'.format(smgr=smgr))
  smod = cfg[RT_SESSION_MGR][smgr]

  user, tix = smod.get_session(cfg)
  kw = {
    'smgr': smgr,
    'url': None,
    'suffix': '',
    'user': user,
    'referer': request.headers['Referer'],
  }
  if 'url' in request.params:
    kw['url'] = request.params['url']
    suffix='?url=' + urlquote(kw['url'])

  if user:
    kw['user_sessions'] = []
    kw['user_cols'] = smod.COL_NAMES
    now = time()
    for row in smod.user_sessions(user,cfg):
      dsp = []
      for col in row:
        if isinstance(col,float):
          col = format_tmlen(now - col)
        dsp.append(col)
      kw['user_sessions'].append(dsp)
      # TODO: Logout a session
      # TODO: Logout all sessions

  return template('logout',**kw)


def format_tmlen(tt):
  txt = None
  if tt > 86400:
    i = int(tt / 86400)
    if i == 1:
      txt = 'one day'
    else:
      txt = '{:,} days'.format(i)
  elif tt > 3600:
    i = int(tt/3600)
    if i == 1:
      txt = 'one hour'
    else:
      txt = '{} hours'.format(i)
  elif tt > 60:
    i = int(tt/60)
    if i == 1:
      txt = 'one minute'
    else:
      txt = '{} minutes'.format(i)
  else:
    txt = 'a few seconds'
  return txt

@route('/auth')
@route('/auth/<smgr>')
def auth(smgr=DEFAULT_SESSMGR):
  if isinstance(cfg[CF_FIXED_IP_LIST],dict):
    client = butils.http_client(request,cfg)
    addr = client['addr']
    if addr in cfg[CF_FIXED_IP_LIST]:
      user = cfg[CF_FIXED_IP_LIST][addr][0]
      groups = ','.join(cfg[CF_FIXED_IP_LIST][addr][0][1:])

      response.set_header('X-Username', user)
      response.set_header('X-Groups', groups)
      return 'FIXED IP SESSION<br>\nUser: {user}<br>\nGroups: {groups}'.format(user=user,groups=groups)

  if not smgr in cfg[RT_SESSION_MGR]:
    return abort(404,'Missing session manager {smgr}'.format(smgr=smgr))
  smod = cfg[RT_SESSION_MGR][smgr]

  user, sdat = smod.get_session(cfg)
  if user:
    prid = smod.get_provider(sdat)
    cfv = cfg[CF_PROVIDERS][prid]
    grplst = userdb.get_groups(user,cfv[CF_PWCK],cfg)
    groups = ','.join(grplst)

    response.set_header('X-Username', user)
    response.set_header('X-Groups', groups)
    return '{smgr} SESSION<br>\nUser: {user}<br>\nGroups: {groups}'.format(user=user,groups=groups,smgr=smgr)

  abort(401,'Unauthenticated')
