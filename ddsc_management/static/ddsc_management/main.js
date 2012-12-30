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

function add_custom_buttons ($container, data_table, delete_url) {
    if (delete_url) {
        var $delete = $('<button class="btn btn-danger selection-only" disabled="disabled">Delete selected rows</button>');
        $delete.click(function (event) {
            // find out which column contains the PK
            var columns = data_table.fnSettings()["aoColumns"];
            var pk_column_index = -1;
            $.each(columns, function (idx, col) {
                if (col["sName"] == 'pk') {
                    pk_column_index = idx;
                }
            });
            // only continue if we found a PK
            if (pk_column_index != -1) {
                var selected = [];
                data_table.$('tr.row-selected').each(function () {
                    var row_data = data_table.fnGetData(this);
                    selected.push(row_data[pk_column_index]);
                });
                // don't do anything if nothing is selected
                if (selected.length > 0) {
                    show_confirm_modal(
                        "Are you sure?",
                        "Are you sure you want to delete the row(s) with ID = " + selected + "?",
                        function () {
                            $.post(
                                delete_url,
                                {
                                    pks: selected
                                }
                            )
                            .success(function (data, textStatus, jqXHR) {
                                data_table.fnReloadAjax();
                            })
                            .error(function (data, textStatus, jqXHR) {
                                alert('Error while deleting row(s): ' + data.status + ' ' + data.statusText);
                            });
                        }
                    )
                }
            }
        });
        $container.append($delete);
    }
}

function data_tables_fnServerData (sSource, aoData, fnCallback, oSettings) {
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

function init_data_tables () {
    // change data tables to support Twitter Bootstrap styling
    // add .form-search etc to the filter form
    $.fn.dataTableExt.oStdClasses["sFilter"] = "form-search pull-right";
    TableTools.classes["buttons"]["normal"] = "btn";
    TableTools.classes["buttons"]["disabled"] = "disabled";
    //TableTools.classes["collection"]["container"] = "dropdown-menu";
    TableTools.classes["select"]["row"] = "row-selected success";

    $('.data-table').each(function (idx) {
        var $el = $(this);
        var $container = $el.parent();
        // allow passing options via data attributes on the element
        var url = $el.data('url');
        var delete_url = $el.data('delete-url');
        // Note: need to wrap arrays because $.data won't recognize
        // an attribute starting with [ as valid JSON.
        var columns = $.parseJSON($el.data('columns'));
        // always add the Primary Key column
        columns.push({
            "sName": "pk",
            "bVisible": false
        });
        // allow passing any extra options, overriding the defaults below
        var extra_options = $el.data('options');
        if (!extra_options) {
            extra_options = {};
        }
        var default_options = {
            "sDom": "<'row-fluid'<'span3'T><'span3'r><'span6 pull-right'f>t<'row-fluid'<'span6'i><'span6 pull-right'p>><'row-fluid'<'span6 pull-right'l>><'row-fluid custom-buttons'>",
            "asStripeClasses": [],
            "oTableTools": {
                "sRowSelect": "multi",
                "sSwfPath": global.lizard.static_url + "ddsc_management/DataTables-1.9.4/extras/TableTools/swf/copy_csv_xls_pdf.swf",
                "fnRowDeselected": function (nodes) {
                    // disable any buttons operating on selected rows here
                    var $btns = $container.find('.custom-buttons .selection-only');
                    var self = this;
                    $.each($btns, function (idx) {
                        if (self.fnGetSelected().length == 0) {
                            $(this).attr("disabled", "disabled");
                        }
                    });
                },
                "fnRowSelected": function (nodes) {
                    // enable any buttons operating on selected rows here
                    var $btns = $container.find('.custom-buttons .selection-only');
                    var self = this;
                    $.each($btns, function (idx) {
                        if (self.fnGetSelected().length != 0) {
                            $(this).removeAttr("disabled");
                        }
                    });
                },
                "aButtons": [
                    "select_all",
                    "select_none",
                    {
                        "sExtends": "collection",
                        "sButtonText": 'Save <span class="caret" />',
                        "aButtons": [
                            {
                                "sExtends": "copy",
                                "sButtonText": "Copy to clipboard",
                                "bSelectedOnly": true
                            },
                            {
                                "sExtends": "print"
                            },
                            {
                                "sExtends": "csv",
                                "sFileName": "ddsc_export.csv",
                                "bSelectedOnly": true
                            },
                            {
                                "sExtends": "xls",
                                "sFileName": "ddsc_export.xls",
                                "bSelectedOnly": true
                            },
                            {
                                "sExtends": "pdf",
                                "sFileName": "ddsc_export.pdf",
                                "bSelectedOnly": true
                            }
                        ]
                    }
                ]
            },
            "bProcessing": true,
            "bServerSide": true,
            "fnServerData": data_tables_fnServerData
        };
        var required_options = {
            "sAjaxSource": url,
            "aoColumns": columns
        };
        var options = $.extend({}, default_options, required_options, extra_options);
        var data_table = $el.dataTable(options);
        // datatables replaces the old <table> element, so remove the
        // reference
        delete $el;
        // add our custom buttons
        // .custom-buttons element as defined in the sDom option
        var $buttons = $container.find('.custom-buttons');
        add_custom_buttons($buttons, data_table, delete_url);
    });
}

function show_confirm_modal (header, message, confirm_callback) {
    var $modal = $('#confirm-modal');
    $modal.find('.modal-header-label').html(header);
    $modal.find('.modal-body p').html(message);
    $modal.data('confirm_callback', confirm_callback);
    $modal.modal('show');
}

function init_confirm_modal () {
    var $container = $('<div>');
    var template_html = $('#confirm-modal-template').html();
    $container.html(template_html);
    $container.appendTo($('body'));
    var $modal = $container.find('.modal');
    $modal.find('.modal-confirm').click(function (event) {
        var callback = $modal.data('confirm_callback');
        if (typeof callback !== 'undefined') {
            callback(event);
        }
        $modal.modal('hide');
    });
    $modal.modal({
        show: false
    });
}

$(document).ready(function () {
    init_dynamic_forms();
    init_data_tables();
    init_confirm_modal();
});
}(this));