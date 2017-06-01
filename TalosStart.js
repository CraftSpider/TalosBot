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
        'onload': 'talosStart()',
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

function buildLogger() {
    log = log4javascript.getDefaultLogger();
    localStorageAppender = new log4javascript.LocalStorageAppender();
    log.addAppender(localStorageAppender);
}

function init(req) {
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
