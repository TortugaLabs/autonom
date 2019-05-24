#
#
# requirements
#
# authlib==0.11
# google-api-python-client
# google-auth
#

import os
from authlib.client import OAuth2Session
import google.oauth2.credentials
import googleapiclient.discovery
from bottle import route, run, request, response, abort,redirect
import time

ACCESS_TOKEN_URI = 'https://www.googleapis.com/oauth2/v4/token'
AUTHORIZATION_URL = 'https://accounts.google.com/o/oauth2/v2/auth?access_type=offline&prompt=consent'
AUTHORIZATION_SCOPE ='openid email profile'

GROUPSFILE = autonom.GROUPSFILE
CLIENT_ID = 'client-id'
CLIENT_SECRET = 'client-secret'
MAP_FILE = 'map-file'
MAX_SESSION = 'max-session'
SIGNATURE = 'AhGheiF9wooth4Haeizai9oH'
COOKIE = 'xxid'

login_sessions = {}
appcfg = {
  MAX_SESSION: 500
}

def new_provider(opts):
  for key in [CLIENT_ID, CLIENT_SECRET]:
    appcfg[key] = opts[key]

  cfg = {
    autonom.NAME: "Google",
    autonom.HREF: "google"
  }
  if GROUPSFILE in opts:
    appcfg[GROUPSFILE] = opts[GROUPSFILE]
  if MAP_FILE in opts:
    appcfg[MAP_FILE] = opts[MAP_FILE]
  if autonom.NAME in opts:
    cfg[autonom.NAME] = opts[autonom.NAME]
    
  return cfg

def expire_logins():
  expired = []
  now = time.time()
  for sid in login_sessions:
    timer = login_sessions[sid]['timestamp']
    if timer+appcfg[MAX_SESSION] > now:
      continue
    expired.append(sid)
  for sid in expired:
    print("Expiring %s" % sid)
    del login_sessions[sid]

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


@route('/login/google')
def login():
  no_cache()
  uri = request.urlparts
  auth_redirect_uri = '%s://%s/%s' % (uri.scheme, uri.netloc, uri.path + '-auth')
  print('AUTH_REDIRECT_URL: '+auth_redirect_uri)
  
  session = OAuth2Session(CLIENT_ID, CLIENT_SECRET,
			scope=AUTHORIZATION_SCOPE,
			redirect_uri=auth_redirect_uri)
  uri, state = session.create_authorization_url(AUTHORIZATION_URL)
  response.set_cookie(COOKIE,state,secret=SIGNATURE,max_age=appcfg[MAX_SESSION],http_only=True)
  
  login_sessions[state] = {
    'timestamp': time.time()
  }
  if 'url' in request.query:
    login_sessions[state]['url'] = request.query.url
  else:
    login_sessions[state]['url'] = None

  redirect(uri)

@route('/login/google-auth')
def google_auth_redirect():
  no_cache()
  if not 'state' in request.query:
    abort(403,"Missing state parameter")
    return
  state = request.query.state
  expire_logins()

  if not state in login_sessions:
    abort(401,"Invalid state parameter")
    return

  if state != request.get_cookie(COOKIE,secret=SIGNATURE):
    abort(401,"State parameter error")
    return

  if 'url' in login_sessions[state]:
    url = login_sessions[state]['url']
  else
    url = None

  del login_sessions[state]

  session = OAuth2Session(CLIENT_ID, CLIENT_SECRET,
			scope=AUTHORIZATION_SCOPE,
			state=state,
			redirect_uri=AUTH_REDIRECT_URI)
  oauth2_tokens = session.fetch_access_token(
                        ACCESS_TOKEN_URI,            
                        authorization_response=request.url)
  print("TOKENS\n======")
  pprint(oauth2_tokens)
  credentials = google.oauth2.credentials.Credentials(
                oauth2_tokens['access_token'],
                refresh_token=oauth2_tokens['refresh_token'],
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                token_uri=ACCESS_TOKEN_URI)
  oauth2_client = googleapiclient.discovery.build(
                        'oauth2', 'v2',
                        credentials=credentials)
  userinfo = oauth2_client.userinfo().get().execute()
  print("USERINFO\n======")
  pprint(userinfo)

  # Check if the e-mail is valid...
  if not 'email' in userinfo:
    abort(401,'Userinfo error')
    return

  user = map_user(user, appcfg[MAP_FILE])
  if not user:
    abort(401,'Unauthorized')

  grps = autonom.get_groups(user,appcfg)

  return autonom.new_session(user,grps,url)
    

