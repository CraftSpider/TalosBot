
import html.parser as parser
import logging

from . import element as el


log = logging.getLogger("talos.utils.parsers")


def attrs_to_dict(attrs):
    """
        Convert a list of tuples of (name, value) attributes to a single dict of attributes [name] -> value
    :param attrs: List of attribute tuples
    :return: Dict of attributes
    """
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
    """
        HTML Parser subclass to convert an HTML document into a DOM Tree of Nodes
    """

    def __init__(self):
        """
            Initialize the TreeGen parser
        """
        super().__init__()
        self.heads = []
        self.cur = None

    def reset(self):
        """
            Reset the parser, prepares it to receive entirely new input data
        """
        super().reset()
        self.heads = []
        self.cur = None

    def close(self):
        """
            Close the current HTML tree being constructed and returns its heads
        :return: Heads of the parsed input
        """
        super().close()
        return self.heads

    def error(self, message):
        """
            Error handler for the HTML parser
        :param message: Parser error message
        """
        log.error(f"Parser Error: {message}")

    def handle_starttag(self, tag, attrs):
        """
            Handle an element starttag. Opens an element, and prepares to add children if it's not self closing
        :param tag: Element tag
        :param attrs: Element attributes
        """
        element = el.Element(tag, attrs_to_dict(attrs))
        if self.cur is None:
            self.heads.append(element)
        else:
            self.cur.add_child(element)

        if tag not in el.Element.SELF_CLOSING:
            self.cur = element

    def handle_endtag(self, tag):
        """
            Handle an element endtag. Closes the current element if it's not self closing
        :param tag: Element tag
        """
        if tag not in el.Element.SELF_CLOSING:
            self.cur = self.cur.parent

    def handle_data(self, data):
        """
            Handle internal element data. Adds a new Content object to the current Element
        :param data: Element internal data
        """
        data = data.strip()
        if not data:
            return

        content = el.Content(data)
        if self.cur is None:
            self.heads.append(content)
        else:
            self.cur.add_child(content)
