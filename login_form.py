#/usr/bin/env python
from bottle import route, request, response, abort, template
import autonom
import crypt
import sys
import apr1
py3 = sys.version_info.major > 2
if py3:
  from urllib.parse import quote_plus as urlquote, unquote as urlunquote
else:
  from urllib import quote_plus as urlquote, unquote as urlunquote

PASSWDFILE = 'passwdfile'
LOGIN_FORM = 'loginform'
GROUPSFILE = autonom.GROUPSFILE

DEFAULT_FORM = '''
  <html>
    <head>
      <title>Login Form</title>
    </head>
    <body>
      <h1>Login Form</h1>
      {{msg}}
      <form method="post">
	<table>
	  <tr><th>User:</th><td><input name="username" type="text" /></td></tr>
	  <tr><th>Password:</th><td><input name="password" type="password" /></td></tr>
	</table>
	<input name="url" type="hidden" value="{{url}}" />
	<input value="Login" type="submit" />
      </form>
    </body>
  </html>
'''
METHOD_APR1 = '$apr1$'

def login_item_html(pid):
  cfg = autonom.get_provider(pid)
  item = {
    autonom.HREF: 'form/'+str(pid),
    autonom.NAME: cfg[autonom.NAME]
  }
  return item

def new_provider(opts):
  cfg = {
    PASSWDFILE: opts[PASSWDFILE],
    autonom.LOGIN_ITEM_HTML: login_item_html
  }
  if GROUPSFILE in opts:
    cfg[GROUPSFILE] = opts[GROUPSFILE]
  if autonom.NAME in opts:
    cfg[autonom.NAME] = opts[autonom.NAME]
  else:
    cfg[autonom.NAME] = 'Login Form'
  return cfg

def get_templ(pid):
  cfg = autonom.get_provider(pid)

  templ = DEFAULT_FORM
  if LOGIN_FORM in cfg:
    templ = cfg[LOGIN_FORM]
  return templ

def htpasswd_crypt(cleartxt,salt):
  if salt[:len(METHOD_APR1)] == METHOD_APR1:
    # Use MD5 method from Apache httpd
    salt = salt[len(METHOD_APR1):len(METHOD_APR1)+8]
    return apr1.apr1md5(cleartxt, salt, METHOD_APR1)
  else:
    return crypt.crypt(cleartxt,salt)
  
def check_login(username, password, cfg):
  try:
    with open(cfg[PASSWDFILE],"r") as fp:
      for line in fp:
       x = line.strip().split(':',2)
       if len(x) < 2:
        continue
       if str(x[0]).lower() != str(username).lower():
        continue
       if htpasswd_crypt(password,x[1]) == x[1]:
        return x[0],autonom.get_groups(x[0],cfg)
       break
  except IOError as err:
    sys.stderr.write("Error opening file %s\n" % cfg[PASSWDFILE])
  return None,None

@route('/login/form/<pid>')
def login_form(pid):
  pid = int(pid)
  templ = get_templ(pid)
  url = ''
  if 'url' in request.query:
    url = urlquote(request.query['url'])
  return template(templ,url=url,msg='')


@route('/login/form/<pid>',method='POST')
def do_login(pid):
  pid = int(pid)
  cfg = autonom.get_provider(pid)

  username = request.forms.get('username')
  password = request.forms.get('password')
  url = urlunquote(request.forms.get('url'))
  
  user,grps = check_login(username, password, cfg)
  if user:
    # succesful...
    return autonom.new_session(user,grps,url)

  templ = get_templ(pid)

  return template(templ,url=url,msg="Login Failed")




