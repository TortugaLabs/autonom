#/usr/bin/env python
import sys
py3 = sys.version_info.major > 2
import hashlib as md5
# ~ from pprint import pprint

def apr1md5(password, salt, magic = '$apr1$'):
    if py3:
      password = password.encode('utf-8')
      salt = salt.encode('utf-8')
      magic = magic.encode('utf-8')
  
    m = md5.md5()
    # /* The password first, since that is what is most unknown */ /* Then our magic string */ /* Then the raw salt */
    m.update(password + magic + salt)

    # /* Then just as many characters of the MD5(pw,salt,pw) */
    mixin = md5.md5(password + salt + password).digest()
    if py3:
      for i in range(0, len(password)):
        m.update(bytes([mixin[i % 16]]))
    else:
      for i in range(0, len(password)):
        m.update(mixin[i % 16])


    # /* Then something really weird... */
    # Also really broken, as far as I can tell.  -m
    i = len(password)
    while i:
      if py3:
        if i & 1:
            m.update(b'\x00')
        else:
            m.update(bytes([password[0]]))
      else:
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
    if py3:
      itoa64 = b'./0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
      rearranged = b''
      for a, b, c in ((0, 6, 12), (1, 7, 13), (2, 8, 14), (3, 9, 15), (4, 10, 5)):
        v = final[a] << 16 | final[b] << 8 | final[c]
        for i in range(4):  
            rearranged += bytes([itoa64[v & 0x3f]]); v >>= 6
      v = final[11]
      for i in range(2):      
        rearranged += bytes([itoa64[v & 0x3f]]); v >>= 6
    else:
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

    # ~ from pprint import pprint
    # ~ pprint(rearranged)
    if py3:
      return "".join(map(chr,magic + salt + b'$' + rearranged))
    else:
      return magic + salt + '$' + rearranged

if __name__ == '__main__':
  if len(sys.argv) == 3:
    print(apr1md5(sys.argv[1],sys.argv[2],'$apr1$'))
  else:
    print("Usage:\n\tcmd passwd salt\n")
