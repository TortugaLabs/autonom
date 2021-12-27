<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Autonom Logout</title>
    <!-- link rel="stylesheet" href="style.css" -->
    <!-- script src="script.js" --><!-- /script -->
  </head>
  <body>
    <h1>Autonom Logout</h1>
    %if user:
      <p>You are logged in as {{user}}.</p>
      <p><a href="/logout/confirm/{{smgr}}{{suffix}}">Confirm Logout?</a></p>
      <p><a href="{{referer}}">Back</a></p>
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
      <p><a href="/login/{{smgr}}{{suffix}}">Login</a></p>
    %end
  </body>
</html>
