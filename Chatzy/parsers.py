
import re
import logging
import html.parser as hparser
import chatzy.utils as utils
import chatzy.errors as errors

log = logging.getLogger("talos.parsers")


class FormInputParser(hparser.HTMLParser):

    def __init__(self):
        super().__init__()
        self.inputs = []
        self.forms = 0
        self.in_form = False

    def handle_starttag(self, tag, attrs):
        if tag == "form" and self.forms == 0:
            self.in_form = True
        elif tag == "form" and self.forms > 0:
            raise errors.ParserException("Do not currently support multiple forms in page")

        if self.in_form and (tag == "input" or tag == "select"):
            data = {}
            for attr in attrs:
                data[attr[0]] = attr[1]
            self.inputs.append(data)

    def handle_endtag(self, tag):
        if tag == "form":
            self.in_form = False
            self.forms += 1

    def close(self):
        super().close()
        if not self.in_form and self.inputs:
            return self.inputs
        elif not self.inputs:
            raise errors.ParserException("Form parser found no forms")
        else:
            raise errors.ParserException("Form parser closed before form end")


var_finder = re.compile(r"(?:var )?((?:X\d{4}.?)*(?:X\d{4})) ?= ?([^=][^;]+);")


class ScriptVarsParser(hparser.HTMLParser):

    def __init__(self):
        super().__init__()
        self.scripts = 0
        self.in_script = False
        self.vars = []

    def handle_starttag(self, tag, attrs):
        if tag == "script" and self.scripts == 0:
            for attr in attrs:
                if attr[0] == "src":
                    return
            self.in_script = True
        elif tag == "script" and self.scripts > 0:
            raise errors.ParserException("Multiple scripts currently not supported")

    def handle_endtag(self, tag):
        if tag == "script" and self.in_script:
            self.in_script = False
            self.scripts += 1

    def handle_data(self, data):
        if self.in_script:
            self.vars += var_finder.findall(data)

    def close(self):
        super().close()
        if not self.in_script and self.vars:
            return self.vars
        elif not self.vars:
            raise errors.ParserException("Script parser found no scripts")
        else:
            raise errors.ParserException("Script parser closed before script end")


class MessageParser(hparser.HTMLParser):

    def __init__(self):
        super().__init__()
        self.type = ""
        self.author = ""
        self.color = ""
        self.text = ""
        self.in_b = False
        self.code = ""
        self.timestamp = 0

    def handle_starttag(self, tag, attrs):
        # print("Encountered start tag:", tag, attrs)
        if tag == "p":
            self.type = attrs[0][1]
        if tag == "b":
            self.in_b = True
            self.color = utils.Color(re.sub(r"color:#|;", "", attrs[0][1]))

    def handle_endtag(self, tag):
        # print("Encountered end tag:", tag)
        if tag == "b":
            self.in_b = False

    def handle_data(self, data):
        # print("Encountered data:", data)
        if self.in_b:
            self.author = data
        else:
            self.text += data.strip(": ")

    def handle_comment(self, data):
        code, data = data.split(":")
        self.code = code
        if code == "XS":
            self.timestamp = data
        elif code == "XCP":
            self.text = data

    def close(self):
        super().close()
        if self.code == "XS":
            return utils.Message(self.type, self.author, self.color, self.text)
        elif self.code == "XCP":
            return utils.Message(self.code, "server", utils.Color(0), self.text + " was kicked")
        else:
            log.warning("Unknown Server Code: " + self.code)
            return utils.Message("server", "server", utils.Color(0), "Unknown Server Message")
