var Commands = {
	"toggleLock": function() {
		toggleChatLock();
	},
	"hello": function() {
		postMessage("Hello World!");
	},
	"sext": function() {
		postMessage("[x]You concatenate my strings ;) ;) ;)[/x]");
	},
	"seen": function(user) {
		searchMessages("{V:" + user[0] + "}");
	}
};

function postMessage(message) {
    // X92.value = message;
    // X342();
    X279(message);
}

function privateMessage(name, message) {
    postMessage("/pm \"" + name + "\" " + message);
    console.log("\"" + message + "\" sent to " + name);
}

//Note, only sends the message to online users.
function globalMessage(message) {
    var users = X330.split("\n");
    for (var i = 1; i <= users[0]; i++) {
		user = users[i].split("	");
		privateMessage(user[0], message);	//Replace the 0 with other numbers to grab different values. 2 is last leave/exit, 4 is status, 5 is location.
    }
}

function searchMessages(term) {
	postMessage("/find " + term);
	
}

///requires re-init of JSBot. Automate that?
function changeName(name) {
    X292('X387');

    setTimeout(function() {
        X481.value = name;
        X544.onsubmit();
    }, 1000);
}

function closeChat() {
	X279("/close");
}

function openChat() {
	X279("/open");
}

function toggleChatLock() {
	if(X105.X398) {
		X279("/open");
	} else {
		X279("/close");
	}
}

function readChat() {
	var Messages = X17("X138").innerHTML.split("\n");
	for (var i = 1; i < Messages.length; i++) {
		var Message = Messages[i];
		if (Message.match(/: \^(\w+)(?:\s(.+))?/)) { //Instead of matching a set list of commands, match the word then check it against a dict?
			var Command = RegExp.$1;
			var Args = RegExp.$2.split(/[\s]|&nbsp;<span/);
			if(window["Commands"][Command]) {
				window["Commands"][Command](Args);
			}
		}
	}
	
	
	X17("X138").innerHTML = '<P class="b">Previous messages parsed (press ESC to re-parse page)</P>\n';
	X783 = false;
}

function test() {
    
    
    
    /*var x = 0;
    postLoop = setInterval(function() {
        postMessage("This is minute " + x);
        x++;
        if (x >= 60) {
            clearInterval(postLoop);
        }
    }, 60000);*/
}
