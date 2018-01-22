
import math
import re
import discord
from discord.embeds import Embed, EmbedProxy, EmptyEmbed, _EmptyEmbed


_EmptyEmbed.__len__ = lambda self: 0
EmptyField = EmbedProxy({"text": "", "name": "", "inline": False})


def _suffix(d):
    """
        Determine the suffix for a date
    :param d: day to determine suffix of
    :return: string of suffix
    """
    return 'th' if 11 <= d <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(d % 10, 'th')


def _custom_strftime(strf, t):
    """
        Custom string-format function to allow a time format to contain day in the form `1st`, `2nd`, `3r`, etc.
    :param strf: Format string
    :param t: Time to format with the string
    :return: formatted string
    """
    return t.strftime(strf).replace('{D}', str(t.day) + _suffix(t.day))


class PaginatedEmbed(Embed):
    """
        Does fancy embed paginating. Will make a single embed with all given fields, except if it becomes too long.
        A single field being too long becomes Field, Field continued. A whole embed too long, Embed continued.
        Extends Embed, and can be used identical to a normal embed if wanted. In that case, passing it to send will
        result in only the first page being sent, whether there are one or many pages.
    """

    __slots__ = Embed.__slots__ + ("_built_pages", "_max_size", "repeat_title", "repeat_desc", "repeat_author")

    MAX_TOTAL = 6000
    MAX_TITLE = 256
    MAX_DESCRIPTION = 2048
    MAX_FIELDS = 25
    MAX_FIELD_NAME = 256
    MAX_FIELD_VALUE = 1024
    MAX_FOOTER = 2048
    MAX_AUTHOR = 256

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._max_size = kwargs.get("max_size", self.MAX_TOTAL)
        self._built_pages = []
        self.repeat_title = False
        self.repeat_desc = False
        self.repeat_author = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return self._built_pages.pop(0)
        except IndexError:
            raise StopIteration

    @property
    def size(self):
        # Base size
        size = len(self.title) + len(self.description) + len(self.author.name)
        # Add size for each field
        for field in self._fields:
            name = len(field.name)
            value = len(field.value)
            size += name + value
            # Add any extra title lengths for field overflow. value stays the same.
            if value > self.MAX_FIELD_VALUE:
                size += (name + 6) * (value // 1024)
        # Calculate the size of things that are repeated on each page.
        pages = self.num_pages
        for i in range(pages):
            if self.repeat_title:
                size += len(self.title)
            if self.repeat_desc:
                size += len(self.description)
            if self.repeat_author:
                size += len(self.author.name)
            size += len(self.footer.text.format(i, pages))
            if self._timestamp != discord.Embed.Empty:
                size += len(_custom_strftime("%a %b {D}, %Y at %I:%M %p", self._timestamp))
        # And that's the total size now.
        return size

    @property
    def num_pages(self):
        max_pages = 10
        page = 1
        while math.floor(math.log(max_pages, 10)) != math.floor(math.log(page, 10)):
            max_pages = page
            page = 1
            cur_size = len(self.title) + len(self.description) + len(self.author.name)
            for field in self.fields:
                field_size = len(field.name) + len(field.value)
                footer_size = len(self.footer.text.format(page, max_pages))
                if cur_size + field_size + footer_size > self._max_size or field == EmptyField:
                    page += 1
                    cur_size = (len(self.title) if self.repeat_title else 0) + \
                               (len(self.description) if self.repeat_desc else 0) + \
                               (len(self.author.name) if self.repeat_author else 0)
                cur_size += field_size
        if len(self.fields) > 0 and self.fields[-1] == EmptyField:
            page -= 1
        return page

    @property
    def pages(self):
        return self._built_pages.copy()

    @property
    def colour(self):
        return getattr(self, "_colour", [EmptyEmbed])

    @colour.setter
    def colour(self, value):
        if isinstance(value, (list, tuple)):
            self._colour = value
        if isinstance(value, (discord.Colour, _EmptyEmbed)):
            self._colour = [value]
        elif isinstance(value, int):
            self._colour = [discord.Colour(value=value)]
        else:
            raise TypeError('Expected list, tuple, discord.Colour, int, or Embed.Empty but received %s instead.' %
                            value.__class__.__name__)

    color = colour

    @property
    def footer(self):
        return EmbedProxy(getattr(self, "_footer", {"text": "Page {}/{}"}))

    @property
    def fields(self):
        out = []
        for field in getattr(self, "_fields", []):
            if len(field["value"]) > self.MAX_FIELD_VALUE:
                value = field["value"]
                name = field["name"]
                inline = field["inline"]
                for i in range(int(math.ceil(len(value) / self.MAX_FIELD_VALUE))):
                    match = re.search(r"[\n.][^\n.]*?(?!\.)$", value[:self.MAX_FIELD_VALUE + 1])
                    if match is not None:
                        out.append(EmbedProxy({"name": name, "value": value, "inline": inline}))
                        value = value[match.start():]
                    else:
                        out.append(EmbedProxy({"name": name, "value": value, "inline": inline}))
                        value = value[self.MAX_FIELD_VALUE + 1:]
                    if i == 0:
                        name = name + " cont."
            else:
                out.append(EmbedProxy(field))
        return out

    def add_field(self, *, name, value, inline=False):
        super().add_field(name=name, value=value, inline=inline)

    def to_dict(self):
        pass  # TODO

    def close_page(self):
        try:
            self._fields.append(EmptyField)
        except AttributeError:
            self._fields = [EmptyField]

    def close(self):
        max_pages = self.num_pages
        page = 1
        cur_len = 0
        cur_fields = 0
        cur_colour = 0
        num_colours = len(self.colour)
        embed = discord.Embed(title=self.title, description=self.description, colour=self.colour[cur_colour],
                              timestamp=self.timestamp)
        cur_colour += 1
        if self.author.name:
            embed.set_author(name=self.author.name, url=self.author.url, icon_url=self.author.icon_url)
        for field in self.fields:
            field_len = len(field.name) + len(field.value)
            footer_len = len(self.footer.text.format(page, max_pages))
            cur_fields += 1
            if cur_fields % 25 == 0 or field == EmptyField or cur_len + field_len + footer_len > self._max_size:
                embed.set_footer(text=self.footer.text.format(page, max_pages), icon_url=self.footer.icon_url)
                self._built_pages.append(embed)
                cur_len = 0
                page += 1
                embed = discord.Embed(title=self.title if self.repeat_title else discord.Embed.Empty,
                                      description=self.description if self.repeat_desc else discord.Embed.Empty,
                                      colour=self.colour[cur_colour % num_colours], timestamp=self.timestamp)
                cur_colour += 1
                if self.repeat_author and self.author.name:
                    embed.set_author(name=self.author, url=self.author.url, icon_url=self.author.icon_url)
            cur_len += field_len
            if field != EmptyField:
                embed.add_field(name=field.name, value=field.value, inline=field.inline)
        if embed.title or embed.description or len(embed.fields) != 0 or len(self._built_pages) == 0:
            embed.set_footer(text=self.footer.text.format(max_pages, max_pages), icon_url=self.footer.icon_url)
            self._built_pages.append(embed)


if __name__ == "__main__":
    tembed = PaginatedEmbed()
    tembed.add_field(name="Test", value="Temp")
    print(tembed)
