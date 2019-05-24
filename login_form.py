#/usr/bin/env python
from bottle import route, request, response, abort, template
import autonom
import crypt
import md5
import sys
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

def md5crypt(password, salt, magic):
    # /* The password first, since that is what is most unknown */ /* Then our magic string */ /* Then the raw salt */
    m = md5.new()
    m.update(password + magic + salt)

    # /* Then just as many characters of the MD5(pw,salt,pw) */
    mixin = md5.md5(password + salt + password).digest()
    for i in range(0, len(password)):
        m.update(mixin[i % 16])

    # /* Then something really weird... */
    # Also really broken, as far as I can tell.  -m
    i = len(password)
    while i:
        if i & 1:
            m.update('\x00')
        else:
            m.update(password[0])
        i >>= 1

    final = m.digest()

    # /* and now, just to make sure things don't run too fast */
    for i in range(1000):   
        m2 = md5.md5()      
        if i & 1:           
            m2.update(password)
        else:               
            m2.update(final)
                            
        if i % 3:           
            m2.update(salt) 
                            
        if i % 7:           
            m2.update(password)
                            
        if i & 1:           
            m2.update(final)
        else:               
            m2.update(password)
                            
        final = m2.digest() 
                            
    # This is the bit that uses to64() in the original code.
                            
    itoa64 = './0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
                            
    rearranged = ''         
    for a, b, c in ((0, 6, 12), (1, 7, 13), (2, 8, 14), (3, 9, 15), (4, 10, 5)):
        v = ord(final[a]) << 16 | ord(final[b]) << 8 | ord(final[c])
        for i in range(4):  
            rearranged += itoa64[v & 0x3f]; v >>= 6
                            
    v = ord(final[11])      
    for i in range(2):      
        rearranged += itoa64[v & 0x3f]; v >>= 6
                            
    return magic + salt + '$' + rearranged

def htpasswd_crypt(cleartxt,salt):
  if salt[:len(METHOD_APR1)] == METHOD_APR1:
    # Use MD5 method from Apache httpd
    salt = salt[len(METHOD_APR1):len(METHOD_APR1)+8]
    return md5crypt(cleartxt, salt, METHOD_APR1)
  else:
    return crypt.crypt(cleartxt,salt)
  
def check_login(username, password, cfg):
  try:
    with open(cfg[PASSWDFILE],"r") as fp:
      for line in fp:
       x = line.strip().split(':',2)
       print('user: %s\npasswd: %s\ninput: %s\n' % (username,password,x))
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




