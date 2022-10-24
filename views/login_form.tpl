<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{desc}} | autonom v{{version}}</title>
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
	    <td><input type="text" name="username" onkeydown='handleEnter(event)'></td>
	  </tr>
	  <tr>
	    <td>Password:</td>
	    <td><input type="password" name="password" id="pwfld"></td>
	  </tr>
	  <tr>
	    <th rowspan=2>
	      <a href="{{cancel_url}}"><button type="button">Cancel</button></a>
	      <input type="submit" name="do_login" value="Login">
	    </th>
	  </tr>
	</table>
      </form>
      <script>
	function handleEnter(event) {
	  if (event.key==="Enter") {
	    pwfld = document.getElementById("pwfld");
	    pwfld.focus();
	    event.preventDefault();
	  }
	}
      </script>
  </body>
</html>
