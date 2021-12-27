#!/usr/bin/python3
from argparse import ArgumentParser, Action
import sys
import random
from hashlib import md5
# We need a crypt module, but Windows doesn't have one by default.  Try to find
# one, and tell the user if we can't.
try:
  import crypt
except ImportError:
  try:
    import fcrypt as crypt
  except ImportError:
    sys.stderr.write("Cannot find a crypt module.  "
			"Possibly http://carey.geek.nz/code/python-fcrypt/\n")
    sys.exit(1)

def gen_salt(len = 8):
  """Returns a string of <len> randome letters"""
  letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/.'
  salt = ''
  for x in range(len):
    salt = salt + random.choice(letters)
  return salt

def ck_passwd(passwd):
  if len(passwd) == 0:
    sys.stderr.write("Password: ")
    sys.stderr.flush()
    pwd_in = sys.stdin.readline()
    return pwd_in.rstrip()
  return ' '.join(passwd)

def std_crypt(prefix, slen, salt,passwd):
  passwd = ck_passwd(passwd)
  if salt is None:
    salt = prefix + gen_salt(slen)
  else:
    if prefix == '' and salt[0] == '$':
      raise Exception('Invalid salt value %s' % salt)
    elif not salt[0] == '$':
      salt = prefix + salt
    elif not salt.startswith(prefix):
      raise Exception('Invalid salt "%s" for the specified mode' % salt)

  pwd_out = crypt.crypt(passwd, salt)
  return pwd_out

def md5crypt(password, salt, magic='$apr1$'):
    # /* The password first, since that is what is most unknown */ /* Then our magic string */ /* Then the raw salt */
    m = md5()

    if isinstance(password, str): password = password.encode()
    if isinstance(salt, str): salt = salt.encode()
    if isinstance(magic, str): magic = magic.encode()

    m.update(password + magic + salt)

    # /* Then just as many characters of the MD5(pw,salt,pw) */
    mixin = md5(password + salt + password).digest()

    for i in range(0, len(password)):
      m.update(bytes([mixin[i % 16]]))

    # /* Then something really weird... */
    # Also really broken, as far as I can tell.  -m
    i = len(password)
    while i:
      if i & 1:
        m.update(b'\x00')
      else:
        m.update(bytes([password[0]]))
      i >>= 1

    final = m.digest()

    # /* and now, just to make sure things don't run too fast */
    for i in range(1000):
      m2 = md5()
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
      v = final[a] << 16 | final[b] << 8 | final[c]
      for i in range(4):
        rearranged += itoa64[v & 0x3f]; v >>= 6

    v = final[11]
    for i in range(2):
      rearranged += itoa64[v & 0x3f]; v >>= 6

    return rearranged

def apr1_crypt(salt,passwd):
  passwd = ck_passwd(passwd)

  prefix = '$apr1$'

  if salt is None:
    salt = gen_salt(8)
  else:
    if salt.startswith(prefix):
      salt = salt[len(prefix):]
    elif salt[0] == '$':
      raise Exception('Invalid salt value %s' % salt)
    i = salt.find('$')
    if i != -1: salt= salt[:i]

  # ~ import subprocess
  # ~ x = subprocess.run(['openssl','passwd','-salt',salt,'-apr1',passwd], capture_output=True)
  # ~ print(x)

  pwd_out = prefix + salt + '$' + md5crypt(passwd, salt)
  return pwd_out

def apr1_digest(user,realm,passwd):
  passwd = ck_passwd(passwd)
  m = md5()
  m.update((user + ":" + realm + ":" + passwd).encode())
  pwd_out = realm + ":" + m.digest().hex()
  return pwd_out

def main(mode='des',passwd=None,salt=None,htdigest=None):
  out = None

  if mode == 'des':
    out = std_crypt('',2,salt,passwd)
  elif mode == 'md5':
    out = std_crypt('$1$',8,salt,passwd)
  elif mode == 'sha256':
    out = std_crypt('$5$',16,salt,passwd)
  elif mode == 'sha512':
    out = std_crypt('$6$',16,salt,passwd)
  elif mode == 'htpasswd':
    out = apr1_crypt(salt,passwd)
  elif mode == 'htdigest':
    if htdigest is None:
      raise Exception('htdigest mode request "-D user realm" options')
    elif not len(htdigest) == 2:
      raise Exception('htdigest request that both user and realm names be specified')
    (user,realm) = htdigest
    if not salt is None:
      raise Exception("Can not specify salt in htdigest mode")
    out = apr1_digest(user,realm,passwd)
  else:
    raise Exception('Unknown mode: %s' % mode)

  print(out)

class FooAction(Action):
  def __init__(self, option_strings, dest, **kwargs):
    super(FooAction, self).__init__(option_strings, dest, **kwargs)
  def __call__(self, parser, namespace, values, option_string=None):
    setattr(namespace, 'mode', 'htdigest')
    setattr(namespace, self.dest, values)

if __name__ == '__main__':
  cli = ArgumentParser(description="password generator")
  cli.add_argument('-0','--des',
                    action='store_const', dest='mode', const="des",
                    help='Use DES encryption')
  cli.add_argument('-1','--md5',
                    action='store_const', dest='mode', const="md5",
                    help='Use MD5 hash')
  cli.add_argument('-5','--sha256',
                    action='store_const', dest='mode', const="sha256",
                    help='Use SHA256 hash')
  cli.add_argument('-6','--sha512',
                    action='store_const', dest='mode', const="sha512",
                    help='Use SHA512')
  cli.add_argument('-A','--htpasswd',
                    action='store_const', dest='mode', const="htpasswd",
                    help='Use Apache httpd md5 variant')
  cli.add_argument('-D', '--htdigest',
                    action=FooAction,nargs=2,dest='htdigest',metavar='STR',
                    help='Apache http digest authentication (user realm)')
  cli.add_argument('-S','--salt',
                    action='store', dest='salt', default=None,
                    metavar='SALT', help='Initial salt')
  cli.add_argument('passwd', metavar='PASSWD', nargs='*',
                    help='Optional password, otherwise read from stdin')
  opts = cli.parse_args()
  if opts.mode is None:
    opts.mode = 'des'
    if not opts.salt is None:
      # no mode, but salt is specified... identify the mode
      # from the salt...
      if opts.salt[:3] == '$1$':
        opts.mode = 'md5'
      elif opts.salt[:3] == '$5$':
        opts.mode = 'sha256'
      elif opts.salt[:3] == '$6$':
        opts.mode = 'sha512'
      elif opts.salt[:6] == '$apr1$':
        opts.mode = 'htpasswd'

  main(opts.mode, opts.passwd, opts.salt, opts.htdigest)



