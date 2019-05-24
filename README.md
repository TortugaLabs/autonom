# autonom

Autonom is plugable authentication server based on the [Bottle][bottlepy] framework
for the [nginx][nginx] auth_request authentication module.

See my article on the [auth request module][authrequest] on how is this supposed to work.

Autonom features:

- [nginx][nginx] auth request compatbility
- plugable authentication modules
- user|group data

The following modules are available:

- login_



[bottlepy]: http://bottlepy.org/
[nginx]: http://nginx.org/
[authrequest]: https://www.0ink.net/2019/05/10/nginx_mod_authrequest.html