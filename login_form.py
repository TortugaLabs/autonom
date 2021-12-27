#/usr/bin/env python
from bottle import route, template, request, redirect
from const import *
from urllib.parse import quote_plus as urlquote
import userdb

NAME = 'login_form'
DEFAULTS = {
  CF_DESC: 'Login form',
  CF_HREF: '/login_form/{id}/{smgr}{suffix}',
  CF_ROUTE: '/login_form/<prid>/<smgr>',
  CF_VIEW: 'login_form',
  CF_PWCK: None,
}
cfg = None

# ~ def cfgparse(cfv,key,val):
  # ~ return False

def init(cfv):
  route(cfv[CF_ROUTE],'GET',lf_dialog)
  route(cfv[CF_ROUTE],'POST',lf_post)

def lf_dialog(prid,smgr):
  cfv = cfg[CF_PROVIDERS][prid]
  kw = {
    'url': None,
    'msg': None,
  }
  if 'url' in request.params: kw['url'] = request.params['url']
  if 'msg' in request.params: kw['msg'] = request.params['msg']
  return template(cfv[CF_VIEW], **kw, **cfv)

def lf_post(prid,smgr):
  if not smgr in cfg[RT_SESSION_MGR]:
    return abort(404,'Missing session manager {smgr}'.format(smgr=smgr))
  smod = cfg[RT_SESSION_MGR][smgr]

  cfv = cfg[CF_PROVIDERS][prid]
  kw = {
    'url': None,
    'msg': None,
  }
  if 'url' in request.params: kw['url'] = request.params['url']
  if 'msg' in request.params: kw['msg'] = request.params['msg']
  if kw['url'] is None:
    suffix = ''
  else:
    suffix = '?url=' + urlquote(kw['url'])

  if not 'do_login' in request.forms:
    # User is cancelling...
    return redirect('/login' + suffix)

  if ('username' in request.forms) and ('password' in request.forms):
    user, extra = userdb.check_password(request.forms['username'],
                                          request.forms['password'],
                                          cfv[CF_PWCK],cfg)
    if not user is None:
      tixid = smod.new_session(user, prid, cfg)
      if kw['url'] is None: return redirect('/hello/{smgr}'.format(smgr=smgr))
      return redirect(url)

    if extra is None:
      kw['msg'] = 'pwck error'
    else:
      kw['msg'] = extra
  else:
    kw['msg'] = 'Login error'

  return template(cfv[CF_VIEW],**kw, **cfv)



