#
# IP access lists
#
import fnmatch

def simple_match(pattern,item):
  return pattern == item

def not_simple_match(pattern,item):
  return pattern != item

def pattern_match(pattern,item):
  return fnmatch.fnmatch(item, pattern)

def not_pattern_match(pattern,item):
  return not fnmatch.fnmatch(item, pattern)

def is_pattern(item):
  for char in ('*', '?', '['):
    if char in item: return True
  return False

def parse_list(iptext):
  iplist = []
  for ip in iptext.split():
    if ip == '' or ip == '!':  continue
    if ip[0] == '!':
      ip = ip[1:]
      if is_pattern(ip):
        iplist.append( (not_pattern_match, ip) )
      else:
        iplist.append( (not_simple_match, ip) )
    else:
      if is_pattern(ip):
        iplist.append( (pattern_match, ip) )
      else:
        iplist.append( (simple_match, ip) )

  return iplist

def check_list(addr, iplist):
  # ~ print('addr: {addr}'.format(addr=addr))
  for checker,pattern in iplist:
    # ~ print('pat: {pat} | check: {checker}'.format(pat=pattern,checker=checker))
    if checker(pattern,addr): return True
  return False

# ~ iplist = parse_list('127.0.0.1 192.168.* \n10.0.0.* !80*')

# ~ print(check_list('192.168.10.10',iplist))
# ~ print(check_list('80.30.22.10',iplist))
# ~ print(check_list('180.30.22.10',iplist))

