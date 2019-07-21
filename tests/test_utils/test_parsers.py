
import spidertools.common.parsers as parsers


def test_site_parse():
    site = """
<html>
  <head>
    <script src="testsrc" />
  </head>
  <body>
    <div class="blah" id="id">
      <p>This is a test paragraph</p>
    </div>
  </body>
</html>"""
    gen = parsers.TreeGen()
    gen.feed(site)
    result = gen.close()
    assert len(result) == 1
    root = result[0]
    assert root.tag == "html"
    assert len(root.child_nodes) == 2

    head = root.first_child
    assert head.tag == "head"
    script = head.first_child
    assert script.tag == "script"
    assert script.get_attribute("src") == "testsrc"

    body = root.child_nodes[1]
    assert body.tag == "body"
    div = body.first_child
    assert div.tag == "div"
    assert div.id == "id"
    assert div.has_class("blah")
    p = div.first_child
    assert p.tag == "p"
    assert p.innertext == "This is a test paragraph"
