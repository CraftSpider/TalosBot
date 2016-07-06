var fs = require("fs");

function fileReader(fileName) {
	var fileText = fs.readFileSync(fileName, "utf8");
	return fileText;
}

console.log(fileReader("OverlordTalos.js"));