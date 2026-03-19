import pytest

from src.handler import (
    FieldsContext, AnkiInterface, addon_field_filter, handle_answer,
    _format_field_result, _classify_error, _calc_input_width, _clear_correct_value_as_reviewer,
)
from src.config import ConfigService, ConfigKey
from tests.anki_mocks_test import TestReviewer, TestCard

AnkiInterface.strip_HTML = lambda i: i

class FilterContext:

    def __init__(self, c_ord: int):
        self._card = TestCard()
        self._card.ord = c_ord - 1

    def card(self):
        return self._card


def test_other_filter():
    data = """This is a <span class="cloze" 
     data-ordinal="1">test</span"""
    res = addon_field_filter(data, "Text", "other-filter", FilterContext(1))

    assert res == data


def test_filter():
    data = """
        This is a <span class="cloze-inactive" 
     data-ordinal="1">test</span>&nbsp;<br>With some toher <span class="cloze" 
     data-cloze="fields" data-ordinal="2">[...]</span>.<br>And two fields on the  
     <span class="cloze-inactive" data-ordinal="1">same</span><br><br>But not  
     type.<br>And field with <span class="cloze-inactive"  
     data-ordinal="3">double</span> field upd field upd 
    """

    res = addon_field_filter(data, "Text", "fill-blanks", FilterContext(2))

    print(res)
    assert 'id="ansval0" type="hidden" value="fields"' in res
    assert 'typeans0' in res


def test_filter2():
    data = """
This is a <span class="cloze-inactive" data-ordinal="1">test</span>&nbsp;<br>With some toher <span class="cloze" data-ordinal="2">fields</span>.<br>And two fields on the <span class="cloze-inactive" data-ordinal="1">same</span><br><
br>But not type.<br>And field with <span class="cloze-inactive" data-ordinal="3">double</span> field upd field upd
    """

    res = addon_field_filter(data, "Text", "fill-blanks", FilterContext(2))

    print(res)


def test_multiple():
    data = """
This is a <span class="cloze" data-ordinal="1">test</span>&nbsp;<br>With some toher <span class="cloze-inactive" data-ordinal="2">fields</span>.
<br>And two fields on the <span class="cloze" data-ordinal="1">same</span><br><br>But not type.
<br>And field with <span class="cloze-inactive" data-ordinal="3">double</span> field upd field upd
    """

    res = addon_field_filter(data, "Text", "fill-blanks", FilterContext(1))

    assert 'id="ansval0" type="hidden" value="test"' in res
    assert 'id="ansval1" type="hidden" value="same"' in res
    assert 'ansval2' not in res


def test_filter_with_hint():
    data = """This is a <span class="cloze-inactive" data-ordinal="1">test</span>&nbsp;<br>With some toher <span class="cloze-inactive" data-ordinal="2">fields</span>.<br>And two fields on the <span class="cloze-inactive" data-ordinal="1">same</s
pan><br><br>But not type.<br>And field with <span class="cloze" data-cloze="double" data-ordinal="3">[comma]</span> hint
    """

    res = addon_field_filter(data, "Text", "fill-blanks", FilterContext(3))

    assert 'value="double"' in res
    assert 'placeholder="comma"' in res


def test_answer_correct():
    content = """
<style>.card {
    font-family: arial;
    font-size: 20px;
    text-align: center;
    color: black;
    background-color: white;
}
.cloze {
    font-weight: bold;
    color: blue;
}
.nightMode .cloze {
    color: lightblue;
}
</style>This is a <span class="cloze-inactive" data-ordinal="1">test</span>&nbsp;<br>With some toher <span class="cloze-inactive" data-ordinal="2">fields</span>.<br>And two fields on the <span class="cloze-inactive" data-ordinal="1"
>same</span><br><br>But not type.<br>And field with <span class="cloze" data-ordinal="3">double</span> hint
<br>
A value in the back field upd field upd

    """

    FieldsContext.entry_number = 1
    FieldsContext.answers = ["double"]
    res = handle_answer(content, TestCard(), "reviewAnswer")

    assert '<span class="cloze st-ok">double</span>' in res

def test_answer_wrong():
    content = """
<style>.card {
    font-family: arial;
    font-size: 20px;
    text-align: center;
    color: black;
    background-color: white;
}
.cloze {
    font-weight: bold;
    color: blue;
}
.nightMode .cloze {
    color: lightblue;
}
</style>This is a <span class="cloze-inactive" data-ordinal="1">test</span>&nbsp;<br>With some toher <span class="cloze-inactive" data-ordinal="2">fields</span>.<br>And two fields on the <span class="cloze-inactive" data-ordinal="1"
>same</span><br><br>But not type.<br>And field with <span class="cloze" data-ordinal="3">double</span> hint
<br>
A value in the back field upd field upd
    """

    FieldsContext.entry_number = 1
    FieldsContext.answers = ["something-else"]
    res = handle_answer(content, TestCard(), "reviewAnswer")

    assert "st-expected" in res
    assert "st-error" in res

# --------------------------------- From previous version - tests --------------------------------------------

def test_nocloze():
    data = """
    <span class="cloze-inactive" data-cloze="fields" data-ordinal="2">
        Single value
        Multiline
     </span>
    """

    res = addon_field_filter(data, "Text", "fill-blanks", FilterContext(2))

    assert ('Single value' in res)
    assert 'ansval0' not in res


def test_with_quotes():
    data = """
        A small step for a man, <br>a big 
        <span class="cloze" data-cloze="one&#x28;&quot;q&quot;&#x2C;&#x20;&#x27;step&#x27;&#x29;" data-ordinal="1">[...]</span>, 
        <span class="cloze" data-cloze="&#x2E;&#x2E;" data-ordinal="1">[...]</span>..
.<br> <span class="cloze-inactive" data-ordinal="2">plainText</span>
        """

    res = addon_field_filter(data, "Text", "fill-blanks", FilterContext(1))

    print(res)

    assert """<input id="ansval0" type="hidden" value="one(&quot;q&quot;, 'step')"/>""" in res


def test_withRegexStr():
    data = """
        Some content here <span class="cloze" data-cloze="with&#x20;&#x5B;&#x20;&#x5C;&#x5C;t&#x5C;&#x5C;n&#x5C;&#x5C;x&#x5C;&#x5C;r&#x5C;&#x5C;f&#x5D;" data-ordinal="1">[...]</span>
    """

    res = addon_field_filter(data, "Text", "fill-blanks", FilterContext(1))

    print(res)

    assert """\\\\t\\\\n\\\\x\\\\r\\\\f""" in res


def test_field_result_uppercase_error():
    _orig = ConfigService.load_config
    ConfigService.load_config = lambda key: False if key == ConfigKey.IGNORE_CASE else _orig(key)
    try:
        result = _format_field_result('milano', 'Milano')
        assert 'st-case-error' in str(result)
    finally:
        ConfigService.load_config = _orig


def test_field_result_ignore_case():
    _orig = ConfigService.load_config
    ConfigService.load_config = lambda key: True if key == ConfigKey.IGNORE_CASE else _orig(key)
    try:
        result = _format_field_result('milano', 'Milano')
        assert 'st-error' not in str(result)
        assert 'st-ok' in str(result)
        assert 'Milano' in str(result)
    finally:
        ConfigService.load_config = _orig


def test_multiple_with_hint():
    data = """
Probleme mit der Sprache -&gt;&gt; <span class="cloze" data-cloze="Probleme" data-ordinal="1">[Pro...]</span> <span class="cloze-inactive" data-ordinal="2">mit</span> <span class="cloze" data-cloze="der" data-ordinal="1">[de...]</sp
an> <span class="cloze-inactive" data-ordinal="2">Sprache</span> After
    """

    res = addon_field_filter(data, "Text", "fill-blanks", FilterContext(1))

    print(res)
    assert ('typeans0' in res)
    assert 'placeholder="Pro..."' in res
    assert ('mit' in res)


# --------------------------------- _calc_input_width tests ------------------------------------------

def test_input_width_matches_text_length():
    assert _calc_input_width("hello", "") == 6  # len + 1

def test_input_width_minimum():
    assert _calc_input_width("a", "") == 3  # min is 3

def test_input_width_uses_hint_if_longer():
    assert _calc_input_width("ab", "longer hint") == 12  # len("longer hint") + 1

def test_input_width_long_text():
    assert _calc_input_width("a very long answer", "") == 19


# --------------------------------- _clear_correct_value tests ---------------------------------------

def test_clear_value_strips_br():
    result = _clear_correct_value_as_reviewer("hello<br>world")
    assert result == "hello world"

def test_clear_value_strips_nbsp():
    result = _clear_correct_value_as_reviewer("hello&nbsp;world")
    assert result == "hello world"

def test_clear_value_escapes_quotes():
    result = _clear_correct_value_as_reviewer('say "hi"')
    assert result == "say &quot;hi&quot;"

def test_clear_value_strips_zero_width_space():
    result = _clear_correct_value_as_reviewer("a\u200bb")
    assert result == "ab"

def test_clear_value_strips_whitespace():
    result = _clear_correct_value_as_reviewer("  hello  ")
    assert result == "hello"


# --------------------------------- _format_field_result edge cases ----------------------------------

def test_field_result_strips_whitespace():
    result = _format_field_result("  hello  ", "  hello  ")
    assert 'st-ok' in str(result)

def test_field_result_empty_strings():
    result = _format_field_result("", "")
    assert 'st-ok' in str(result)

def test_field_result_html_escaped():
    result = _format_field_result("<script>", "expected")
    assert '<script>' not in str(result)
    assert '&lt;script&gt;' in str(result)

def test_field_result_ignore_case_shows_original_expected():
    _orig = ConfigService.load_config
    ConfigService.load_config = lambda key: True if key == ConfigKey.IGNORE_CASE else _orig(key)
    try:
        result = str(_format_field_result("HELLO", "Hello"))
        assert 'st-ok' in result
        assert 'Hello' in result
    finally:
        ConfigService.load_config = _orig

def test_field_result_ignore_case_mismatch():
    _orig = ConfigService.load_config
    ConfigService.load_config = lambda key: True if key == ConfigKey.IGNORE_CASE else _orig(key)
    try:
        result = str(_format_field_result("wrong", "Right"))
        assert 'st-error' in result
        assert 'Right' in result
        assert 'wrong' in result
    finally:
        ConfigService.load_config = _orig


# --------------------------------- _classify_error tests --------------------------------------------

def test_classify_case_error():
    assert _classify_error("hello", "Hello") == 'st-case-error'
    assert _classify_error("WORLD", "world") == 'st-case-error'

def test_classify_punctuation_error():
    assert _classify_error("hello world", "hello, world") == 'st-punctuation-error'
    assert _classify_error("test-value", "test value") == 'st-punctuation-error'
    assert _classify_error("one two", "one  two") == 'st-punctuation-error'

def test_classify_punctuation_and_case_error():
    assert _classify_error("hello world", "Hello, World") == 'st-punctuation-error'

def test_classify_real_error():
    assert _classify_error("wrong", "right") == 'st-error'
    assert _classify_error("abc", "xyz") == 'st-error'

def test_field_result_case_error_in_answer():
    _orig = ConfigService.load_config
    ConfigService.load_config = lambda key: False if key == ConfigKey.IGNORE_CASE else _orig(key)
    try:
        result = str(_format_field_result("hello", "Hello"))
        assert 'st-case-error' in result
        assert 'st-expected' in result
    finally:
        ConfigService.load_config = _orig

def test_field_result_punctuation_error_in_answer():
    result = str(_format_field_result("hello world", "hello, world"))
    assert 'st-punctuation-error' in result
    assert 'st-expected' in result


# --------------------------------- handle_answer edge cases ----------------------------------------

def test_handle_answer_wrong_phase():
    res = handle_answer("<p>test</p>", TestCard(), "reviewQuestion")
    assert res == "<p>test</p>"

def test_handle_answer_no_fields():
    FieldsContext.entry_number = 0
    res = handle_answer('<span class="cloze">word</span>', TestCard(), "reviewAnswer")
    assert 'word' in res
    assert 'st-ok' not in res

def test_handle_answer_mismatched_spans():
    FieldsContext.entry_number = 1
    FieldsContext.answers = ["one", "two"]
    content = '<span class="cloze">only-one</span>'
    res = handle_answer(content, TestCard(), "reviewAnswer")
    assert 'st-ok' not in res
    assert 'st-error' not in res


# --------------------------------- FieldsContext state tests ----------------------------------------

def test_fields_context_reset_on_filter():
    FieldsContext.entry_number = 99
    FieldsContext.answers = ["leftover"]

    data = '<span class="cloze" data-ordinal="1">[...]</span>'
    addon_field_filter(data, "Text", "fill-blanks", FilterContext(1))

    assert FieldsContext.answers == []

def test_fields_context_no_filter_preserves_state():
    FieldsContext.entry_number = 5
    FieldsContext.answers = ["preserved"]

    addon_field_filter("no cloze here", "Text", "other-filter", FilterContext(1))

    assert FieldsContext.entry_number == 5
    assert FieldsContext.answers == ["preserved"]
