
import html.parser as parser
import utils.element as el


def attrs_to_dict(attrs):
    out = {}
    for attr in attrs:
        if out.get(attr[0]) is None:
            out[attr[0]] = attr[1]
        else:
            if not isinstance(out[attr[0]], list):
                out[attr[0]] = [out[attr[0]]]
            out[attr[0]].append(attr[1])
    return out


class TreeGen(parser.HTMLParser):

    def __init__(self):
        super().__init__()
        self.heads = []
        self.cur = None

    def reset(self):
        super().reset()
        self.heads = []
        self.cur = None

    def close(self):
        super().close()
        return self.heads

    def error(self, message):
        print("Parser Error:", message)

    def handle_starttag(self, tag, attrs):
        element = el.Element(tag, attrs_to_dict(attrs))
        if self.cur is None:
            self.heads.append(element)
        else:
            self.cur.add_child(element)

        if tag not in el.Element.SELF_CLOSING:
            self.cur = element

    def handle_endtag(self, tag):
        if tag not in el.Element.SELF_CLOSING:
            self.cur = self.cur.parent

    def handle_data(self, data):
        data = data.strip()
        if not data:
            return

        content = el.Content(data)
        if self.cur is None:
            self.heads.append(content)
        else:
            self.cur.add_child(content)
