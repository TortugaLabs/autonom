import os

def _version():
  with open(os.path.dirname(os.path.realpath(__file__))+'/VERSION','r') as fp:
    v = fp.read()
  return v.strip()

VERSION = _version()

if __name__ == '__main__':
  print('('+VERSION+')')
