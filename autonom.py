#/usr/bin/env python
from bottle import route, run, request, response, abort, template, redirect
import time
import uuid
import sys
py3 = sys.version_info.major > 2
if py3:
  from urllib.parse import quote_plus as urlquote
else:
  from urllib import quote_plus as urlquote

COOKIE_NAME = 'autonom_session'
SIGNATURE = 'IeRouth7oozae8AhZyH'
PROVIDERS = 'providers'
MAX_SESSION = 'max_session'
PRE_LOGIN_HOOK = 'pre_login_hook'
LOGIN_PAGE_HTML = 'login_page_html'
LOGIN_ITEM_HTML = 'login_item_html'
LOGOUT_PAGE_HTML = 'logout_page_html'
LOGOUT_MSG = 'logout-msg'
GROUPSFILE = 'groupsfile'
IDGEN = 'idgen'
AUTH_HOOK = 'auth-hook'

HREF = 'href'
NAME = 'name'

session_db = {}
settings = {
  MAX_SESSION: 3600,
  LOGOUT_PAGE_HTML: '''
    <html>
     <head>
      <title>Logout</title>
     </head>
     <body>
      <h1>Logout</h1>
      <hr/>
        <a href="/">Home</a>
	<a href="/login/">Login</a>
      <hr/>
      % if user:
        Logged "{{user}}" out ({{', '.join(groups)}})
	<hr/>
      % end
     </body>
    </html>
  ''',
  LOGIN_PAGE_HTML: '''
    <html>
      <head>
        <title>Login Page</title>
      </head>
      <body>
        <h1>Login Page</h1>
	Select a login provider:
	<ul>
	  % for item in providers:
	    <li><a href="{{item["href"]}}{{url}}">{{item["name"]}}</a></li>
	  % end
	</ul>
      </body>
    </html>
    ''',
  PROVIDERS: {}
}

data = {
  IDGEN: 0
}

def genid():
  pid = data[IDGEN]
  data[IDGEN] = data[IDGEN] + 1
  return pid 

def setcfg(key,value):
  settings[key] = value

def get_provider(pid):
  return settings[PROVIDERS][pid]

def register_provider(pdat):
  pid = genid()
  settings[PROVIDERS][pid] = pdat
  return pid

def get_groups(user, cfg):
  groups = []
  if not GROUPSFILE in cfg:
    return groups
  user = str(user).lower()
  try:
    with open(cfg[GROUPSFILE],"r") as fp:
      for line in fp:
       x = line.split(':',2)
       if len(x) < 2:
        continue
       members = str(x[1]).lower().split()
       if user in members:
        groups.extend([x[0]])
  except IOError as err:
    sys.stderr.write("Error opening file %s\n" % cfg[GROUPSFILE])
  return groups

def expire_sessions():
  expired = []
  now = time.time()
  for sid in session_db:
    timer,user,groups,start = session_db[sid]
    if timer+settings[MAX_SESSION] > now:
      continue
    expired.append(sid)
  for sid in expired:
    print("Expiring %s" % sid)
    del session_db[sid]

def new_session(user, groups, url=None):
  expire_sessions()
  print('Creating new session: %s (%s)' % (user, ', '.join(groups)))
  
  while True:
    newid = str(uuid.uuid4())
    if not newid in session_db:
      break

  if 'X-Forwarded-Host' in dict(request.headers):
    domain = request.headers['X-Forwarded-Host'].split('.')
    domain = domain[-2:]
    domain = '.'.join(domain)
  else:
    domain = request.headers['Host']

  session_db[newid] = (time.time(),user,groups,time.time())
  response.set_cookie(COOKIE_NAME,newid,secret=SIGNATURE,httponly=True,domain=domain,path="/")

  if url:
    redirect(url)
  return "New session created for %s\n" % user

def get_session():
  sid = request.get_cookie(COOKIE_NAME, secret=SIGNATURE)
  if sid:
    expire_sessions()
    if sid in session_db:
      timer,user,groups,start = session_db[sid]
      session_db[sid] = (time.time(),user,groups,start)	# Update the session timer...
      return user,groups
  return None, None

def del_session():
  sid = request.get_cookie(COOKIE_NAME, secret=SIGNATURE)
  if sid:
    expire_sessions()
    if sid in session_db:
      del session_db[sid]

def no_cache():
  response.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
  response.set_header('Pragma','no-cache')
  response.set_header('Expires', '-1')

@route('/auth')
def auth():
  if AUTH_HOOK in settings:
    res = settings[AUTH_HOOK]()
    if res:
      return res

  user,groups = get_session()
  if user:
    response.set_header('X-Username', user)
    response.set_header('X-Groups', groups)
    return "Active Session: %s\nGroups: %s\n" % (user,groups)
  abort(401,"Unathenticated")

@route('/login/')
def web_login():
  user,groups = get_session()
  if user:
    return "<pre>\nActive Session: %s\nGroups: %s\n</pre>\n" % (user,groups)

  for prov in settings[PROVIDERS]:
    if PRE_LOGIN_HOOK in settings[PROVIDERS][prov]:
      ret = settings[PROVIDERS][prov][PRE_LOGIN_HOOK](prov)
      if ret:
        return ret

  url = ''
  if 'url' in request.query:
    url = "?url=" + urlquote(request.query['url'])
  providers = []
  for pp in settings[PROVIDERS]:
    if LOGIN_ITEM_HTML in settings[PROVIDERS][pp]:
      item = settings[PROVIDERS][pp][LOGIN_ITEM_HTML](pp)
    elif HREF in settings[PROVIDERS][pp] and NAME in settings[PROVIDERS][pp]:
      item = {
       HREF: settings[PROVIDERS][pp][HREF],
       NAME: settings[PROVIDERS][pp][NAME]
      }
    else:
      continue
    providers.extend([item])

  if len(providers) == 1:
    # If we only have one provider we simply switch...
    href = providers[0][HREF]
    if href[:7] == 'http://' or href[:8] == 'https://':
      pass
    elif href[0] == '/':
      pass
    else:
      href = request.urlparts.path + href + url
    redirect(href)

  return template(settings[LOGIN_PAGE_HTML],providers=providers,url=url)

@route('/logout')
def web_logout():
  user,groups = get_session()
  if user:
    del_session()
  else:
    user=None
    groups=[]
  return template(settings[LOGOUT_PAGE_HTML],user=user,groups=groups)

if __name__ == "__main__":
  run(host='0.0.0.0', port=8080)

