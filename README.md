# autonom

Autonom is plugable authentication server based on the [Bottle][bottlepy] framework
for the [nginx][nginx] auth_request authentication module.

See my article on the [auth request module][authrequest] on how is this supposed to work.

Autonom features:

- [nginx][nginx] auth request compatbility
- plugable authentication modules
- user|group data

The following modules are available:

- login_form : simple HTML login form.
- ident_sso : SSO based on an identd daemon response
- gauth : Google OpenID Connect authentication

# TODO

- ident_sso should have an option to authenticate after clicking a link (instead of automatic)
- logout should accept an URL to redirect user elsewhere


[bottlepy]: http://bottlepy.org/
[nginx]: http://nginx.org/
[authrequest]: https://www.0ink.net/2019/05/10/nginx_mod_authrequest.html
