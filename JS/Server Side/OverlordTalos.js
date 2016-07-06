var http = require('http');
var fs = require("fs");

http.createServer(function (request, response) {

	console.log(request);
	if(request.method == "GET") {
		//Send HTTP header with OK status, type plaintext.
		response.writeHead(200, {
			'Content-Type': 'application/javascript',
			'Access-Control-Allow-Origin': 'http://chatzy.com'
		});

		var CurrVersion = fileReader("OverlordTalos.js");

		//Send response body
		response.write(CurrVersion);
		response.end();

	} else {
		response.writeHead(404);
	}

}).listen(8081);

function fileReader(fileName) {
	fs.readFileSync(fileName, "utf8");
}

console.log('Server running at http://localhost:8081/');