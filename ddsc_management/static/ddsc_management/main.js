(function (global) {
function init_dynamic_form ($el) {
    var id = $el.attr('id');
    if (id) {
        var $submit = $el.find('input[type=submit], button[type=submit]');
        $submit.click(function (event) {
            event.preventDefault();
            var $form = $el.find('form');
            $.post(
                $form.attr('action'),
                $form.serialize()
            )
            .success(function (data) {
                var $new_el = $(data).find('#' + id);
                // Replace the old element containing the form with the
                // new one.
                // .replaceWith() internally calls .remove(), which
                // should properly unbind all event handlers.
                $el.replaceWith($new_el);
                // rebind this event handler again
                init_dynamic_form($new_el);
            })
            .error(function (data) {
                $el.replaceWith('<div>Error while submitting form.</div>');
            });
        });
    }
    else {
        console.error(
            'Encountered a form which has ".dynamic-form" set, but no ' +
            'unique "id" attribute: this form can not be made dynamic.'
        );
    }
}

function init_dynamic_forms () {
    $('.dynamic-form').each(function (idx) {
        init_dynamic_form($(this));
    });
}

function init_data_tables () {
    $('.data-table').each(function (idx) {
        $(this).dataTable({
            "sDom": "<'row'<'span'T><'span pull-right'f>r>t<'row-fluid'<'span'i><'span pull-right'p>>",
            "oTableTools": {
                "sSwfPath": global.lizard.static_url + "ddsc_management/DataTables-1.9.4/extras/TableTools/swf/copy_csv_xls_pdf.swf",
                "aButtons": [
                    "copy",
                    "print",
                    {
                        "sExtends": "collection",
                        "sButtonText": 'Save <span class="caret" />',
                        "aButtons": [
                            {
                                "sExtends": "csv",
                                "sFileName": "ddsc_export.csv"
                            },
                            {
                                "sExtends": "xls",
                                "sFileName": "ddsc_export.xls"
                            },
                            {
                                "sExtends": "pdf",
                                "sFileName": "ddsc_export.pdf"
                            }
                        ]
                    }
                ]
            },
            "bProcessing": true,
            "sAjaxSource": '/api/sources/',
            "sAjaxDataProp": "table_data"
        });
    });
}

$(document).ready(function () {
    init_dynamic_forms();
    init_data_tables();
});
}(this));