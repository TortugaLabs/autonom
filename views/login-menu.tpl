<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Autonom Login Menu</title>
    <!-- link rel="stylesheet" href="style.css" -->
    <!-- script src="script.js" --><!-- /script -->
    % if not active and len(providers) == 1:
    <!-- REFRESH ME -->
    % end
  </head>
  <body>
    % if active:
      <h1>Active Session</h1>
      Session is already running.
      <table>
	<tr><td>User:</td><td>{{user}}</td></tr>
	<tr><td>Ticket:</td><td>{{ticket}}></td></tr>
	<tr><td>Groups:</td><td>{{groups}}</td></tr>
      </table>
      <a href="/autonom/logout{{suffix}}">Logout</a>
    % else:
      <h1>Autonom Login Menu</h1>
      <ul>
	% for prov in providers:
	<li>
	  <a href="{{prov['href']}}">
	    {{prov['desc']}}
	  </a>
	</li>
	% end
      </ul>
    % end
  </body>
</html>
