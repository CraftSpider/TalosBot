const MAIN_URL = "https://rawgit.com/CraftSpider/TalosBot/master/"; //URL to load Commands from
const API_URL = "https://rawgit.com/CraftSpider/ChatzyAPI/master/"; //URL to load ChatzyAPI from

var requirements = [
    {
        'src': MAIN_URL + 'log4javascript.js',
        'onload':'buildLogger()',
        'id':'LoggerScript',
        'message': null,
    },
    {
        'src': API_URL + 'ChatzyWrappers.js',
        'onload': null,
        'id':'ChatzyWrappers',
        'message': 'ChatzyWrappers Loading',
    },
    {
        'src': MAIN_URL + 'Talos.js',
        'onload': null,
        'id':'MainScript',
        'message': 'Talos Loading',
    },
    {
        'src': MAIN_URL + 'Commands.js',
        'onload':'CommandsLoaded = true',
        'id':'CommandScript',
        'message': 'Commands Loading',
    }
]

/*
    ------------------
    Required Functions
    ------------------
*/

function makeElement(name, attrs) {
    var ele = document.createElement(name);
    for (var key in attrs) {
        if (attrs.hasOwnProperty(key)) {
            ele.setAttribute(key, attrs[key]);
        }
    }
    return ele;
}

/*
    -------------------
    Initialization Code
    -------------------
*/

/*function loggerInit() {
    console.log("Logger Initializing");
    
    var Logger = makeElement('script', {'type':'text/javascript',
                                    'src': MAIN_URL + 'log4javascript.js',
                                    'onload':'buildLogger()',
                                    'id':'LoggerScript'});
    document.head.appendChild(Logger);
}*/

function buildLogger() {
    log = log4javascript.getDefaultLogger();
    localStorageAppender = new log4javascript.LocalStorageAppender();
    log.addAppender(localStorageAppender);
}

/*function wrapperInit() {
    log.debug("ChatzyWrappers Loading");
    
    var ChatzyAPI = makeElement('script', {'type':'text/javascript',
                                       'src': API_URL + 'ChatzyWrappers.js',
                                       'onload':'commandsInit()',
                                       'id':'ChatzyWrappers'});
    document.head.appendChild(ChatzyAPI);
}

function commandsInit() {
    log.debug("Commands Loading");
    
    var TalosCommands = makeElement('script', {'type':'text/javascript',
                                           'src': MAIN_URL + 'Commands.js',
                                           'onload':'CommandsLoaded = true; talosInit()',
                                           'id':'CommandScript'});
    document.head.appendChild(TalosCommands);
}

function talosInit() {
    log.debug("Talos Loading");
    
    var TalosMain = makeElement('script', {'type':'text/javascript',
                                           'src': MAIN_URL + 'Talos.js',
                                           'onload':'talosStart()',
                                           'id':'MainScript'})
    document.head.appendChild(TalosMain);
}*/

function init(req) {
    console.log(req)
    if (req >= requirements.length) {
        return;
    }
    
    requirement = requirements[req];
    if (requirement.message) {
        log.debug(requirement.message);
    }
    
    var el = makeElement('script', {'type': 'text/javascript',
                         'src': requirement.src,
                         'onload': requirement.onload + "; init(" + (req+1) + ")",
                         'id': requirement.id});
    document.head.appendChild(el);
}

init(0);