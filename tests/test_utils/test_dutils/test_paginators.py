
import datetime as dt
import utils.dutils as dutils


def test_paginated_helpers():

    assert dutils.paginators._suffix(1) is "st"
    assert dutils.paginators._suffix(2) is "nd"
    assert dutils.paginators._suffix(3) is "rd"
    assert dutils.paginators._suffix(4) is "th"

    assert dutils.paginators._suffix(11) is "th"
    assert dutils.paginators._suffix(21) is "st"

    assert dutils.paginators._custom_strftime("{D}", dt.datetime(year=1, month=1, day=1)) == "1st"
    assert dutils.paginators._custom_strftime("{D}", dt.datetime(year=1, month=1, day=2)) == "2nd"
    assert dutils.paginators._custom_strftime("{D}", dt.datetime(year=1, month=1, day=3)) == "3rd"
    assert dutils.paginators._custom_strftime("{D}", dt.datetime(year=1, month=1, day=4)) == "4th"

    assert dutils.paginators._custom_strftime("{D}", dt.datetime(year=1, month=1, day=11)) == "11th"
    assert dutils.paginators._custom_strftime("{D}", dt.datetime(year=1, month=1, day=21)) == "21st"


def test_paginated_embed():  # TODO: Need to redo due to change to PaginatedEmbed
    page = dutils.PaginatedEmbed()

    # Test empty embed
    assert page.size is 8, "Base size is not 8"
    page.set_footer(text="")
    assert page.size is 0, "Empty Embed isn't size 0"
    page.close()
    assert page.num_pages is 1, "Empty embed has more than one page"
    assert page.num_pages == len(page._built_pages), "Embed num_pages doesn't match number of built pages"

    # # Test simple setters and output
    # colours = [discord.Colour(0xFF00FF)]
    # page = utils.EmbedPaginator(colour=colours)
    #
    # page.set_title("Test Title")
    # page.set_description("Test Description")
    # page.set_author(name="Test#0001", url="http://talosbot.org", avatar="http://test.com")
    # page.set_footer("Test Footer", "http://test.com")
    # page.close()
    # assert page.size == 46, "Embed size incorrect"
    # assert page.pages == 1, "Embed page number incorrect"
    # pages = page.get_pages()
    # assert len(pages) == 1, "Split embed unnecessarily"
    # embed = pages[0]
    # assert embed.title == "Test Title", "Incorrect Title"
    # assert embed.description == "Test Description", "Incorrect Description"
    # assert embed.colour == colours[0], "Embed has wrong colour"
    # assert embed.footer.text == "Test Footer", "Incorrect Footer"
    # assert embed.footer.icon_url == "http://test.com", "Incorrect footer icon"
    # assert embed.author.name == "Test#0001", "Incorrect Author name"
    # assert embed.author.url == "http://talosbot.org", "Incorrect Author url"
    # assert embed.author.icon_url == "http://test.com", "Incorrect Author icon"

    # Test complex setters and output
    pass  # TODO finish testing paginator
