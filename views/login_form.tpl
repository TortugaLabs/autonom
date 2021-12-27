<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>{{desc}}</title>
    <!-- link rel="stylesheet" href="style.css" -->
    <!-- script src="script.js" --><!-- /script -->
  </head>
  <body>
      <h1>{{desc}}</h1>
      % if msg:
      <p>{{msg}}</p>
      % end
      <form method="post">
	% if url:
	  <input type="hidden" name="url" value="{{url}}">
	% end
	<table>
	  <tr>
	    <td>User:</td>
	    <td><input type="text" name="username"></td>
	  </tr>
	  <tr>
	    <td>Password:</td>
	    <td><input type="password" name="password"></td>
	  </tr>
	  <tr>
	    <th rowspan=2>
	      <input type="submit" name="do_login" value="Login">
	      <input type="submit" name="do_cancel" value="Cancel">
	    </th>
	  </tr>
	</table>
      </form>
  </body>
</html>
