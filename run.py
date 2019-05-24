#/usr/bin/env python
import autonom
import login_form
import ident_sso

autonom.register_provider(login_form.new_provider({
  login_form.PASSWDFILE: 'htpasswd.txt',
  autonom.GROUPSFILE: 'htgroup.txt'
}))
autonom.register_provider(ident_sso.new_provider({
  autonom.GROUPSFILE: 'htgroup.txt',
  ident_sso.MAPFILE: 'mappings.txt',
  ident_sso.SERVERPORTMAP: { 9443: 443 },
  ident_sso.ACL: [ '172.18.*', '172.17.*' ]
}))


autonom.run(host='0.0.0.0', port=8080)


