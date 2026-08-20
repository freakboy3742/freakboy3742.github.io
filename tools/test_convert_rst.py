import pytest

from convert_rst import parse_lr


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
