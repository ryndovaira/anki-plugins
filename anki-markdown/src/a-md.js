let mdNotice = '<div class="amd_edit_notice" title="This addon tries to prevent Anki from formatting as HTML">Markdown ON</div>';

function pasteAmdContent(inputValue) {
    let focused = $(':focus');
    if (! focused || focused == 'undefined') {
        return;
    }
    let selection = window.getSelection()
    if (focused.is('input') || focused.is('textarea')) {
        let newVal = (selection && selection != '') ? focused.val().replace(selection, inputValue) : focused.val() + inputValue;
        focused.val(newVal);
    } else {
        let newVal = (selection && selection != '') ? focused.text().replace(selection, inputValue) : focused.text() + inputValue;
        focused.text(newVal);
    }
}

function showMarkDownNotice() {
    let shownNotice = $('.amd_edit_notice').length;
    if (! shownNotice) {
        $('#fields').prepend(mdNotice);
    }    
}

function convertToTextArea(field) {
    var attrs = { };

    var name = field.attr('name');
    var id = field.attr('id');
    var text = field.text();
    console.log('Field: ' + name + '  ' + id);

    var attrs = { };

    $(field).each(function() {
      $.each(this.attributes, function() {
        if (this.name != 'contenteditable' || this.name == 'id') {
            attrs[this.name] = this.value;
        }
      });
    });

    $("<textarea />", attrs)
        .attr('id', 'mirror--' + id)
        .attr('name', 'mirror--' + (name) ? name : id)
        .val(text)
        .keyup( function() {
            field.text($(this).val());
        } )
        .insertAfter('#' + id);

    field.css('display', 'none');
}

/*function convertToTextArea(field) {
    var attrs = { };

    $(field).each(function() {
      $.each(this.attributes, function() {
        if (this.name != 'contenteditable') {
            attrs[this.name] = this.value;
        }
      });
    });

    field.replaceWith(function () {
        return $("<textarea />", attrs)
            .val($(this).text());
    });
}*/

function handleNoteAsMD() {
    $('.field').wrap('<span class=\"amd\"></span>');

    $.each($(".field"), function() {
        convertToTextArea($(this));
    });
}

// ----------------------------- Editor Previewer---------------

let previewInitialized = false;

let showMarkdown = null;
let hideMarkdown = null;

function setPreviewUp() {
    $(`<table id="prev_layout">
        <tr id="fd_w_prev">
            <td id="col_field"></td>
            <td id="prev_toggler" onclick="togglePreview()">            
            </td>
            <td id="preview" class="ui-resizable">
                <i>Markdown preview</i>
            </td>
        </tr>
    </div>`).insertAfter('#topbutsOuter');
    let originalFields = $('#fields').detach();
    $('#col_field').prepend(originalFields);    
    previewInitialized = true;
    showMarkdown = 'S<br/>h<br/>o<br/>w<br/><br/>M<br/>a<br/>r<br/>k<br/>d<br/>o<br/>w<br/>n<br/>';
    hideMarkdown = 'H<br/>i<br/>d<br/>e<br/><br/>M<br/>a<br/>r<br/>k<br/>d<br/>o<br/>w<br/>n<br/><br/>';
    $('#prev_toggler').html(hideMarkdown);
}

function setFieldPreview(name, value) {
    if (! previewInitialized) {
        return;
    }
    let element = $('#pvalue' + name);
    if (! element.length) {
        $('#preview').append(`
            <div id="pfd` + name + `">
                <h4>` + name + `</h4>
                <p id="pvalue`+ name + `"></p>
            </div>
        `);
        element = $('#pvalue' + name);
    }
    element.html(value);
}

function cleanPreview() {
    $('#preview').empty();
}

function togglePreview() {
    let prevDiv = $('#preview');
    if (prevDiv.css('display') == 'none') {
        prevDiv.css('display', '');
        $('#prev_toggler').html(hideMarkdown);
    } else {
        prevDiv.css('display', 'none');
        $('#prev_toggler').html(showMarkdown);
    }
}