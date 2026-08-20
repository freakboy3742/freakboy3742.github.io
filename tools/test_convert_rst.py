import pytest

from convert_rst import parse_lr
from convert_rst import rst_to_markdown


def test_parse_single_line_fields():
    text = (
        "title: Moving to Lektor\n"
        "---\n"
        "pub_date: 2017-04-29 16:00:00\n"
    )
    assert parse_lr(text) == {
        "title": "Moving to Lektor",
        "pub_date": "2017-04-29 16:00:00",
    }


def test_parse_multiline_body_field():
    text = (
        "title: X\n"
        "---\n"
        "body:\n"
        "\n"
        "First paragraph.\n"
        "\n"
        "Second paragraph.\n"
    )
    result = parse_lr(text)
    assert result["body"] == "First paragraph.\n\nSecond paragraph."


def test_parse_field_with_inline_value_and_continuation():
    text = (
        "excerpt: Everyone knows the story.\n"
        "\n"
        "But it isn't always like that.\n"
        "---\n"
        "pub_date: 2017-08-27 12:06:12\n"
    )
    result = parse_lr(text)
    assert result["excerpt"] == "Everyone knows the story.\n\nBut it isn't always like that."


def test_parse_colon_inside_inline_value():
    text = "pub_date: 2017-02-13 7:47:54\n"
    assert parse_lr(text)["pub_date"] == "2017-02-13 7:47:54"


def test_parse_preserves_internal_blank_lines():
    text = (
        "text:\n"
        "\n"
        "Line one.\n"
        "\n"
        "\n"
        "Line four.\n"
    )
    assert parse_lr(text)["text"] == "Line one.\n\n\nLine four."


def test_heading_levels_by_first_adornment_order():
    text = (
        "About Russell\n"
        "~~~~~~~~~~~~~\n"
        "\n"
        "Text.\n"
        "\n"
        "Academia\n"
        "--------\n"
        "\n"
        "More text.\n"
    )
    result = rst_to_markdown(text)
    assert "## About Russell" in result
    assert "### Academia" in result


def test_heading_with_short_underline():
    text = "Call to action 4: Get out your wallets\n~~~~~~~~~~~~~~~~~~~~~~\n\nBody.\n"
    assert "## Call to action 4: Get out your wallets" in rst_to_markdown(text)


def test_horizontal_rule_requires_blank_line_before():
    text = "Intro.\n\n-----\n\nNext section.\n"
    result = rst_to_markdown(text)
    assert "---" in result
    assert "Intro." in result


def test_dashes_directly_under_text_are_headings_not_rules():
    text = "Transcript\n----------\n\nBody.\n"
    result = rst_to_markdown(text)
    assert "## Transcript" in result
    assert result.count("---") == 0


def test_literal_block_becomes_fenced_code():
    text = (
        "Run the following::\n"
        "\n"
        "    $ export PATH=/opt/subversion/bin:$PATH\n"
        "    $ python -c \"import svn.core\"\n"
    )
    result = rst_to_markdown(text)
    assert "```text" in result
    assert "$ export PATH=/opt/subversion/bin:$PATH" in result
    assert "Run the following" in result
    assert result.index("```text") > result.index("Run the following")


def test_raw_html_directive_emitted_verbatim():
    text = (
        "Intro paragraph.\n"
        "\n"
        ".. raw:: html\n"
        "\n"
        "    <iframe width=\"500\" src=\"https://example.com/v\"></iframe>\n"
    )
    result = rst_to_markdown(text)
    assert '<iframe width="500" src="https://example.com/v"></iframe>' in result


def test_image_directive_becomes_markdown_with_attr_classes():
    text = (
        ".. image:: mugshot.png\n"
        "   :width: 33%\n"
        "   :alt: Russell Keith-Magee's mugshot\n"
        "   :align: left\n"
    )
    result = rst_to_markdown(text)
    assert "![Russell Keith-Magee's mugshot](mugshot.png){: .align-left .img-33}" in result


def test_inline_link_single_underscore():
    text = "Use `Lektor <https://getlektor.com>`_ for this.\n"
    assert "[Lektor](https://getlektor.com)" in rst_to_markdown(text)


def test_inline_link_double_underscore():
    text = "See `BeeWare <https://beeware.org>`__ here.\n"
    assert "[BeeWare](https://beeware.org)" in rst_to_markdown(text)


def test_multiple_links_in_one_paragraph():
    text = "A `X <http://a.example>`_ and B `Y <http://b.example>`__ end.\n"
    result = rst_to_markdown(text)
    assert "[X](http://a.example)" in result
    assert "[Y](http://b.example)" in result


def test_inline_literal_becomes_backtick():
    text = "Run ``svn+https`` to clone.\n"
    assert "`svn+https`" in rst_to_markdown(text)


def test_link_inside_heading():
    text = "About `BeeWare <https://beeware.org>`__\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\nBody.\n"
    result = rst_to_markdown(text)
    assert "## About [BeeWare](https://beeware.org)" in result


def test_emphasis_passes_through():
    text = "It *usually* isn't and **never** was.\n"
    assert "It *usually* isn't and **never** was." in rst_to_markdown(text)
