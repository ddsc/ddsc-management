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
    // change data tables to add .form-search etc to the filter form
    $.fn.dataTableExt.oStdClasses["sFilter"] = "form-search pull-right";
    $('.data-table').each(function (idx) {
        var $el = $(this);
        // allow passing options via data attributes on the element
        var url = $el.data('url');
        // Need to wrap because $.data won't recognize an attribute
        // starting with [ as JSON.
        var columns = $.parseJSON($el.data('columns'));
        var extra_options = $el.data('options');
        if (!extra_options) {
            extra_options = {};
        }
        var default_options = {
            "sDom": "<'row-fluid'<'span3'T><'span3'r><'span6 pull-right'f>t<'row-fluid'<'span6'i><'span6 pull-right'p>>",
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
            "bServerSide": true,
            "fnServerData": function (sSource, aoData, fnCallback, oSettings) {
                $.getJSON(
                    sSource,
                    aoData,
                    function (response) {
                        fnCallback(response);
                        // Example of how to parse data from a
                        // custom JSON data source:
                        /*
                        var aaData = [];
                        $.each(response.aaData, function (index, row) {
                            var aData = [];
                            $.each(row, function (key, value) {
                                aData.push(value);
                            });
                            aaData.push(aData);
                        });
                        fnCallback({
                            'aaData': aaData,
                            'iTotalRecords': response.iTotalRecords,
                            'iTotalDisplayRecords': response.iTotalDisplayRecords
                        });
                        */
                    }
                );
            }
        };
        var url_options = {
            "sAjaxSource": url,
            "aoColumns": columns
        };
        var options = $.extend({}, default_options, url_options, extra_options);
        $(this).dataTable(options);
    });
}

$(document).ready(function () {
    init_dynamic_forms();
    init_data_tables();
});
}(this));