let ifEnabled = true;
let shouldIgnoreCase = false;
let shouldIgnoreAccents = false;
let asianCharsEnabled = false;
let typedWords = [];

function checkFieldValue(reference, fieldIndex, event) {
    if (event.key === 'Enter') {
        pycmd("ans");
        return;
    }
    let field = $('#typeans' + fieldIndex);

    if (! ifEnabled) {
        updateTypedValue(fieldIndex);
        return;
    }

    let current = field.val();
    let previous = field.data('lastValue');

    if (suggestNextCharacter(field, current, reference, event)) {
        return;
    }

    current = current.trim();
    if (current == previous) {
        return;
    }

    cleanUpView(field);

    if (current == '' ) {
        field.data('lastValue', '');
        return;
    }

    if (shouldIgnoreCase) {
        current = current.toLowerCase();
        reference = reference.toLowerCase();
    }

    if (shouldIgnoreAccents) {
        current = current.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
        reference = reference.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    }

    if (current == reference) {
        field.addClass('st-ok');
    } else {
        if (reference.startsWith(current)) {
            field.addClass('st-incomplete');
        } else {
            field.addClass(classifyError(current, reference));
        }
    }
    field.data('lastValue', current);
    updateTypedValue(fieldIndex);
}

function cleanUpView(field) {
    field.removeClass('st-ok st-incomplete st-error st-case-error st-punctuation-error');
}

function stripPunctuation(str) {
    return str.replace(/[\s\p{P}]/gu, '');
}

function classifyError(current, reference) {
    if (current.toLowerCase() === reference.toLowerCase()) {
        return 'st-case-error';
    }
    if (stripPunctuation(current) === stripPunctuation(reference)) {
        return 'st-punctuation-error';
    }
    if (stripPunctuation(current).toLowerCase() === stripPunctuation(reference).toLowerCase()) {
        return 'st-punctuation-error';
    }
    return 'st-error';
}

function suggestNextCharacter(field, current, reference, event) {
    if (field.hasClass('st-ok') || field.hasClass('st-error') || current.length >= reference.length) {
        return false;
    }

    if ((event.key === "?" && event.ctrlKey) || (isMacOS() && event.metaKey && event.shiftKey && event.key === '/')) {
        let nextChar = reference.charAt(current.length);
        field.val(current + nextChar);
        return true;
    }

    return false;
}

function isMacOS() {
  return navigator.platform.toUpperCase().indexOf('MAC') >= 0;
}

// ------------- Verification ---------------
function cleanUpTypedWords() {
    typedWords = [];
}

function prepareTypedWords(numFields) {
    for (let i = 0; i < numFields; i++) {
        typedWords.push("");
    }
}

function updateTypedValue(position) {
    let content = $("#typeans" + position).val().trim();
    typedWords[position] = content;
}

// --------------- Options ------------------

function disableInstantFb() {
    ifEnabled = false;
}

function ignoreCaseOnFeedback() {
    shouldIgnoreCase = true;
}

function ignoreAccentsOnFeedback() {
    shouldIgnoreAccents = true;
}

function enableAsianChars() {
    asianCharsEnabled = true;
}

// ------------------------------------

function focusOnFirst() {
    setTimeout(() => {
        try {
            $('#typeans0').focus();
        } catch (error) {
            console.warn(error);
        }        
    }, 300);   
}

function setUpFillBlankListener(expected, typeAnsIndex) {
    const eventType = (asianCharsEnabled) ? "input" : "keyup"
    document.getElementById(`typeans${typeAnsIndex}`).addEventListener(eventType,
      (evt) => checkFieldValue(expected, typeAnsIndex, evt))

    // add extra event for Enter key
    if (eventType === "input") {
        document.getElementById(`typeans${typeAnsIndex}`).addEventListener("keyup", (evt) => {
            if (event.key === 'Enter') {
                pycmd("ans");
            }
        })
    }
}