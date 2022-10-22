# autonom

Autonom is plugable authentication server based on the [Bottle][bottlepy] framework
for the [nginx][nginx] auth_request authentication module.

See my article on the [auth request module][authrequest] on how is this supposed to work.

Autonom features:

- [nginx][nginx] auth request compatbility
- plugable authentication modules
- user|group data

The following modules are available:

Login providers:

- login_form : simple HTML login form.

Backend providers:

- flatfiles
- tlrealms

# TODO

- make it so that we can cache some sessions in memory
  and don't touch the filesystem
- change logout screen in to a 403 page.
- session: delete other tickets, delete specific ticket
- pw change interface
- pw chfn: shell, gecos

# CHANGES

- 2.1.0
  - Added viewport settings for Mobile compatibility
  - change login form layout
- 2.0.1
  - adding pack script
  - adding sample nginx config
  - misc tweaks
  - misc bufixes
  - misc clean-ups
- 2.0.0
  - Mayor rewrite
- 1.0.0
  - Initial version

[bottlepy]: http://bottlepy.org/
[nginx]: http://nginx.org/
[authrequest]: https://www.0ink.net/2019/05/10/nginx_mod_authrequest.html
