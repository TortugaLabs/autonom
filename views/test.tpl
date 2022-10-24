<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Page | (autonom v{{version}}</title>
    <!-- link rel="stylesheet" href="style.css" -->
    <!-- script src="script.js" --><!-- /script -->
  </head>
  <body>
    <h1>Test Page</h1>

    <h2>Headers</h2>
    <table>
      % for hdr in headers:
      <tr>
	<td>{{hdr}}:</td>
	<td>{{headers[hdr]}}</td>
      </tr>
      % end
    </table>

    % if len(http_client):
    <h2>HTTP Client</h2>
    <table>
      % for c in http_client:
      <tr>
	<td>{{c}}:</td>
	<td>{{http_client[c]}}</td>
      </tr>
      % end
    </table>
    % end

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

    <h2>Environ</h2>
    <table>
      % for k in env:
      <tr>
	<td>{{k}}:</td>
	<td>{{env[k]}}</td>
      </tr>
      % end
    </table>
    <hr/>
  </body>
</html>
