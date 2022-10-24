<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Autonom: {{msg}} | autonom v{{version}}</title>
    <!-- link rel="stylesheet" href="style.css" -->
    <!-- script src="script.js" --><!-- /script -->
  </head>
  <body>
    <h1>Autonom: {{msg}}</h1>
    %if user:
      <p>You are logged in as {{user}}.</p>
      <p><a href="/autonom/logout/confirm/{{smgr}}{{suffix}}">Confirm Logout?</a></p>
      %if referer:
      <p><a href="{{referer}}">Back</a></p>
      %end
      <p>All <em>{{smgr}}</em> sessions</p>
      <table border=1>
	<tr>
	  %for col in user_cols:
	    <th>{{col}}</th>
	  %end
	</tr>
        %for session in user_sessions:
	  <tr>
	    %for i in session:
	      <td>{{i}}</td>
	    %end
	  </tr>
	%end
      </table>
    %else:
      <p>You do not have any active sessions</p>
      <p><a href="/autonom/login/{{smgr}}{{suffix}}">Login</a></p>
    %end
  </body>
</html>
