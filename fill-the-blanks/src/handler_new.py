# -*- coding: utf-8 -*-
# Class responsible for the processing
#
# This file is part of fill-the-blanks addon
# @author ricardo saturnino
# -------------------------------------------------------

import os
import re
from typing import Optional

from bs4 import BeautifulSoup
import html


class AnkiInterfaceNew:
    """
        Decouples internal components from Anki, making it easier for unit testing
    """

    staticReviewer = None

    @staticmethod
    def stripHTML(*args):
        raise NotImplementedError("Must be replaced")


currentLocation = os.path.dirname(os.path.realpath(__file__))


class FieldsContext:
    ignore_case = False
    currentFirst = None
    entry_number = 0
    answers: list = list()


def addon_field_filter(field_text: str, field_name: str, filter_name: str, ctx) -> str:
    if filter_name != "fill-blanks":
        return field_text

    # print("**** Field filter: %s on field %s" % (filter_name, field_name))
    # print(field_text)

    FieldsContext.entry_number = 0
    FieldsContext.answers.clear()

    rev_card = ctx.card()

    # print("card ord: %d" % rev_card.ord)

    body = BeautifulSoup(field_text, 'html.parser')

    typein_fields = _traverse_entries(body, rev_card)
    FieldsContext.entry_number = typein_fields

    if typein_fields > 0:
        FieldsContext.currentFirst = "typeans0"

    return str(body)


def _traverse_entries(body, rev_card) -> int:
    typein_fields = 0
    for idx, span in enumerate(body.find_all('span', 'cloze')):
        classes = span['class'] if span.has_attr('class') else []   # TODO remove
        tag_ordinal = span['data-ordinal'] if span.has_attr('data-ordinal') else "-1"
        if tag_ordinal != str(rev_card.ord + 1):
            continue

        cloze_value = span['data-cloze'] if span.has_attr('data-cloze') else span.text
        remaining_text = span.text
        span.replace_with(_apply_typein_value(cloze_value, remaining_text, idx))
        typein_fields += 1
    return typein_fields


def _apply_typein_value(cloze_value: str, extra_text: Optional[str], field_idx: int) -> BeautifulSoup:
    clean_value = _clear_correct_value_as_reviewer(cloze_value)
    has_hint = extra_text and extra_text != cloze_value and extra_text != "[...]"
    hint = extra_text.removeprefix("[").removesuffix("]") if has_hint else ""

    elements = _create_fill_elements(field_idx, clean_value, hint)

    return elements


def _clear_correct_value_as_reviewer(text_beautiful_soup: str):
    """Mostly copy from original reviewer code *as plain text*"""

    # cor = self._mw.col.media.strip(valueAsBeautifulSoupText)      TODO
    cor: str = text_beautiful_soup
    cor = re.sub("(\n|<br ?/?>|</?div>)+", " ", cor)
    cor = cor.replace("&nbsp;", " ")
    cor = cor.replace("\xa0", " ")
    cor = cor.replace('"', '&quot;')

    # Remove zero-width space that might be used between double-colons as a
    # hack to support double-colon content within cloze deletion (prevent
    # hint split); users might add `&ZeroWidthSpace;` in HTML, which
    # BeautifulSoup interprets as unicode `\u200b`:
    cor = cor.replace("\u200b", "")
    cor = cor.strip()
    return cor


def _create_fill_elements(idx: int, text: str, hint: str = "") -> BeautifulSoup:
    hidden = BeautifulSoup("""<input type="hidden" id="ansval%d" value="%s" />""" % (idx, text), "html.parser")
    typein = BeautifulSoup("""<input type="text" id="typeans%d" placeholder="%s" class="ftb %s" />""" %
                           (idx, hint, _get_length_class(text, hint)), "html.parser")
    script = BeautifulSoup(
        """<script type="text/javascript">setUpFillBlankListener($('#ansval%d').val(), %d)</script>""" % (idx, idx),
        'html.parser')

    # placeholder_for_callback_result = BeautifulSoup("""<input type="hidden" id="ansval" value="" />""", "html.parser")

    container_soup = BeautifulSoup("""<span class="ftb-container"></span>""", "html.parser")
    container = container_soup.span

    container.append(hidden)
    container.append(typein)
    container.append(script)
    # container.append(placeholder_for_callback_result)

    return container


def _get_length_class(text: str, hint: str):
    # TODO
    hint_present = hint if hint else ""
    size = max(len(text), len(hint_present))
    return "ftb-md"


def on_show_question():
    reviewer = AnkiInterfaceNew.staticReviewer
    web = reviewer.mw.web
    if FieldsContext.currentFirst:
        web.setFocus()
        web.eval("focusOnFirst();")
    if FieldsContext.entry_number > 0:
        web.eval("cleanUpTypedWords();")
        web.eval("prepareTypedWords(%d);" % FieldsContext.entry_number)


# --------------------------------- Handle answer ----------------------------------------

def handle_answer(answer: str, card, phase: str) -> str:
    if phase != "reviewAnswer":
        return answer

    # print("=== %s %s" % ("Anwser", '=' * 50))
    # print(answer)

    soup = BeautifulSoup(answer, 'html.parser')
    field_ctx = None if FieldsContext.entry_number == 0 else FieldsContext
    span_list = soup.find_all('span', 'cloze')

    if not field_ctx or (len(span_list) != len(field_ctx.answers)):
        return answer

    for idx, span in enumerate(span_list):
        cur_text = span.get_text()
        given = field_ctx.answers[idx]
        span.replace_with(_format_field_result(given, cur_text))

    return str(soup)


def _format_field_result(given: str, expected: str) -> BeautifulSoup:
    given = given.strip()
    expected = expected.strip()
    match_ignore_case = FieldsContext.ignore_case and given.lower() == expected.lower()
    if given == expected or match_ignore_case:
        return BeautifulSoup("<span class='cloze st-ok'>%s</span>" % html.escape(expected), "html.parser")
    return BeautifulSoup("<del class='cloze st-error'>%s</del><ins class='cloze st-expected'>%s</ins>" %
                         (html.escape(given), html.escape(expected)),
                         "html.parser")


def getTypedAnswer(_old):
    reviewer = AnkiInterfaceNew.staticReviewer
    if FieldsContext.entry_number > 0:
        reviewer.web.evalWithCallback("typedWords ? typedWords : []", _onFillBlankAnswer)
    return _old(reviewer)


def _onFillBlankAnswer(val) -> None:
    reviewer = AnkiInterfaceNew.staticReviewer
    if FieldsContext.entry_number > 0:
        FieldsContext.answers = val
    reviewer._showAnswer()


def _createFieldsContext(self, txt, idx) -> FieldsContext:
    # matches = [self._splitHint(txt) for txt in matches]
    # _fieldStates = map(self._extractFieldState, matches)
    # txt = re.sub(reCloze, self.CURRENT_CARD_FIELD_PLACEHOLDER, txt)

    if '[sound:' in txt:
        txt = re.sub(r'\[sound:(\w|\d|\.|\-|_)+?\]', '', txt, flags=re.DOTALL)
