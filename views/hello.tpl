<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Hello Page</title>
    <!-- link rel="stylesheet" href="style.css" -->
    <!-- script src="script.js" --><!-- /script -->
  </head>
  <body>
    <h1>Hello Page</h1>
    <p>Hello {{name}}</p>
    % if session:
    <p>Logged in as {{session}} {{groups}}</p>
    <p>Ticket: {{ticket}}</p>
    <p><a href='/autonom/logout/menu/{{smgr}}'>Logout</a></p>
    % else:
    <p><a href='/autonom/login/{{smgr}}'>Login</a></p>
    % end
    <h2>Request details</h2>
    <table>
      <tr>
	<td>remote address:</td>
	<td>{{remote_addr}}</td>
      </tr>
      <tr>
	<td>remote route:</td>
	<td>{{remote_route}}</td>
      </tr>
      <tr>
	<td>Method:</td>
	<td>{{method}}</td>
      </tr>
      <tr>
	<td>URL:</td>
	<td>{{url}}</td>
      </tr>
      <tr>
	<td>URL args:</td>
	<td>{{url_args}}</td>
      </tr>
      <tr>
	<td>URLparts:</td>
	<td>{{urlparts}}</td>
      </tr>
      <tr>
	<td>Path:</td>
	<td>{{path_info}}</td>
      </tr>
      <tr>
	<td>Query String:</td>
	<td>{{query_string}}</td>
      </tr>
    </table>

    <h2>Headers</h2>
    <table>
      % for hdr in headers:
      <tr>
	<td>{{hdr}}:</td>
	<td>{{headers[hdr]}}</td>
      </tr>
      % end
    </table>

    % if len(cookies):
    <h2>Cookies</h2>
    <table>
      % for c in cookies:
      <tr>
	<td>{{c}}:</td>
	<td>{{cookies[c]}}</td>
      </tr>
      % end
    </table>
    % end

    % if len(query):
    <h2>Query</h2>
    <table>
      % for q in query:
      <tr>
	<td>{{q}}:</td>
	<td>{{query[q]}}</td>
      </tr>
      % end
    </table>
    % end

    % if len(forms):
    <h2>Forms</h2>
    <table>
      % for f in forms:
      <tr>
	<td>{{f}}:</td>
	<td>{{forms[f]}}</td>
      </tr>
      % end
    </table>
    % end

    <h2>Environ</h2>
    <table>
      % for k in env:
      <tr>
	<td>{{k}}:</td>
	<td>{{env[k]}}</td>
      </tr>
      % end
    </table>
  </body>
</html>
