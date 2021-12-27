#
# Module to with useful functionality to write service applications
#
import sys, os, time

TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S %z"
using_syslog = False

# Unbuffered I/O
#
# A lot of times, daemons will run in the background with output
# going to a file or to a pipe
#
# This makes sure that the output is handled immediatly
#
class Unbuffered(object):
  def __init__(self, stream):
     self.stream = stream
  def write(self, data):
     self.stream.write(data)
     self.stream.flush()
  def writelines(self, datas):
     self.stream.writelines(datas)
     self.stream.flush()
  def __getattr__(self, attr):
     return getattr(self.stream, attr)

def unbuffered_io():
  sys.stdout = Unbuffered(sys.stdout)
  sys.stderr = Unbuffered(sys.stderr)

#
# Makes the output of process to be logged on syslog
#
def _io_syslog(fh,tag):
  r,w = os.pipe()
  cpid = os.fork()
  if cpid == 0:
    # Child...
    os.close(w)
    sys.stdin.close()
    sys.stdout.close()
    sys.stderr.close()
    fin = os.fdopen(r)

    # ~ x = open('log-%s.txt' % tag,'w')
    import syslog

    for line in fin:
      line = line.rstrip()
      if not line: continue
      syslog.syslog("%s: %s" % (tag,line))
      # ~ x.write("%s: %s\n" % (tag,line))
      # ~ x.flush()
    sys.exit(0)

  os.close(r)
  os.dup2(w, fh.fileno())
  os.close(w)

def syslog_io(tag):
  global using_syslog

  using_syslog = True
  _io_syslog(sys.stdout,'%s(out)' % tag)
  _io_syslog(sys.stderr,'%s(err)' % tag)

def filelog_io(filename):
  sys.stdin.close()
  sys.stdout.close()
  sys.stdout = open(filename,'a')
  os.dup2(sys.stdout.fileno(),sys.stderr.fileno())

#
# Prepends output with a timestamp
#
def ts_print(msg, mode='stdout'):
  global using_syslog

  if mode == 'stdout':
    io = sys.stdout
  elif mode == 'stderr':
    io = sys.stderr
  else:
    raise ValueError("Invalid ts_print mode: %s" % mode)

  if using_syslog:
    prefix = ''
  else:
    # If not using syslog, we output a time-stamp
    prefix = "[" + time.strftime(TIMESTAMP_FORMAT) + "]:"
  io.write(prefix + msg + "\n")

#
# Makes the current process to run in the background
#
def daemonize():
  newpid = os.fork()
  if newpid != 0: sys.exit(0)
  os.setsid()
  newpid = os.fork()
  if newpid != 0: sys.exit(0)

#
# Save current PID to a file
#
def pidfile(filename):
  with open(filename,"w") as fh:
    fh.write("%d\n" % os.getpid())

#
# Format timestamp
#
def timestamp(ts = None):
  if ts is None: ts = time.time()
  return time.strftime(TIMESTAMP_FORMAT, time.localtime(ts))

if __name__ == "__main__":
  print(timestamp())
  print(timestamp(3455345))
