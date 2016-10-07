
function parseJSON(str, acc) {
    console.log("Function called on " + str);
    console.log("head is " + str[0]);
    var out;
    if (str[0] == '{') {
        console.log("found object");
        str = str.substr(1);
        out = {};
        if (acc) {
            splice = str.indexOf('}') + 2;
            console.log(splice);
            return [parseJSON(str, out), splice];
        }
        return parseJSON(str, out);
    } else if (str[0] == '}') {
        return acc;
    } else if (str[0] == '[') {
        out = [];
    } else if (str[0] == '"') {
        console.log("found string");
        out = "";
        var i = 1;
        while(str[i] != '"') {
            out += str[i];
            i++;
        }
        i++;
        str = str.substr(i);
        if(str[0] == ':') {
            str = str.substr(1);
            if (str[0] == ' ') {
                str = str.substr(1)
            }
            retArr = parseJSON(str, true);
            acc[out] = retArr[0];
            str = str.substr(retArr[1]);
            console.log(str)
            if (str[0] == ',') {
                return parseJSON(str.substr(1), acc);
            } else {
                return acc;
            }
        } else {
            return [out, out.length+2];
        }
    } else if (str[0] == ' ') {
        console.log("found space");
        return parseJSON(str.substr(1), acc);
    } else if (!isNaN(str[0]) || str[0] == '-') {
        console.log("found Number");
        out = "";
        var i = 0;
        while(!isNaN(str[i]) || str[i] == '-') {
            out += str[i];
            i++;
        }
        str = str.substr(i);
        if(str[0] == ':') {
            str = str.substr(1);
            if (str[0] == ' ') {
                str = str.substr(1)
            }
            retArr = parseJSON(str);
            acc[out] = retArr[0];
            str = str.substr(retArr[1]);
            if (str[0] == ',') {
                return parseJSON(str.substr(1), acc);
            } else {
                return acc;
            }
        } else {
            return [+out, out.length];
        }
    } else {
        return acc;
    }
}
