(function (global) {

function wrapped_replace_with (target, data) {
    // root elements with an id can't be found without wrapping first
    // (for some reason)
    var $wrapped = $('<div>' + data + '</div>');
    var $new_el = $wrapped.find('#' + target);
    var $old_el = $('#' + target);
    // Replace the old element containing the form with the
    // new one.
    // .replaceWith() internally calls .remove(), which
    // should properly unbind all event handlers.
    $old_el.replaceWith($new_el);
    // remove the wrapper as well
    $wrapped.remove();
}

function init_dynamic_links () {
    $(document).on('click',
        'a.dynamic-link',
        function (event) {
            var $el = $(this);
            var target = $el.data('target');
            if (!target) {
                console.error(
                    'No target id set, so can not properly determine target element.'
                );
                return;
            }
            event.preventDefault();
            var url = $el.attr('href');
            $.get(url)
            .success(function (data) {
                wrapped_replace_with(target, data);
            })
            .error(function (data) {
                // enforce a full screen refresh
                window.location = url
            });
        }
    );
}

function init_dynamic_forms () {
    function dynamic_submit (event) {
        event.preventDefault();
        var $el = $(this);
        var target = $el.data('target');
        if (!target) {
            target = $el.attr('id');
        }
        if (!target) {
            console.error(
                'No id or target id set, so can not properly determine target element.'
            );
            return;
        }
        var $form = $el;
        $.post($form.attr('action'), $form.serialize())
        .success(function (data) {
            wrapped_replace_with(target, data);
        })
        .error(function (data) {
            $el.replaceWith('<p class="error">Error while submitting form.</p>');
        });
    }

    $(document).on('submit',
        'form.dynamic-form',
        dynamic_submit
    );
}

function add_custom_buttons ($container, data_table, delete_url) {
    if (delete_url) {
        var $delete = $('<button class="btn btn-danger selection-only" disabled="disabled"><i class="icon-trash"></i> Delete selected item(s)</button>');
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
                var oTT = TableTools.fnGetInstance(data_table.get()[0]);
                var selected_data = oTT.fnGetSelectedData();
                $.each(selected_data, function (idx) {
                    selected.push(this[pk_column_index]);
                });
                // don't do anything if nothing is selected
                if (selected.length > 0) {
                    show_confirm_modal(
                        "Are you sure?",
                        "Are you sure you want to delete the item(s) with ID = " + selected + "?",
                        function () {
                            $.post(
                                delete_url,
                                {
                                    pks: selected
                                }
                            )
                            .success(function (data, textStatus, jqXHR) {
                                data_table.fnReloadAjax();
                                // would be nicer if we can retain the selected page here
                                // $.each(data.deleted, function (idx) {
                                    // var pk = this.pk;
                                    // alert(pk);
                                    // //data_table.fnDeleteRow();
                                // });
                            })
                            .error(function (data, textStatus, jqXHR) {
                                alert('Error while deleting item(s): ' + data.status + ' ' + data.statusText);
                            });
                        }
                    );
                }
            }
        });
        $('<div class="span12"/>')
            .wrapInner($delete)
            .appendTo($container);
    }
}

function fix_selection_on_page_change (data_table) {
    data_table.on('page', function (event) {
        var oTT = TableTools.fnGetInstance(data_table.get()[0]);
        oTT.fnSelectNone();
    });
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
    TableTools.classes["select"]["row"] = "row-selected success";
    TableTools.classes["container"] = "DTTT_container btn-group";

    $('.data-table').each(function (idx) {
        var $el = $(this);
        // these are initialised after the table is created,
        // but the reference must be visible in the fnRowDeselected handler
        var $container;
        var $custom_buttons;
        // allow passing options via data attributes on the element
        var url = $el.data('url');
        var delete_url = $el.data('delete-url');
        // Note: need to wrap arrays because $.data won't recognize
        // an attribute starting with [ as valid JSON.
        var columns = $.parseJSON($el.data('columns'));
        // always add the Primary Key column
        columns.push({
            "aTargets": ["pk"],
            "sName": "pk",
            "bVisible": false
        });
        // add the actions column
        columns.push({
            "aTargets": ["details_url"],
            "sName": "details_url",
            "sTitle": "Actions",
            "bSortable": false,
            //"sClass": "no-select",
            "mRender": function (data, type, full) {
                return '<a class="btn btn-mini dynamic-link no-select" href="'+ data +'" data-target="detail-view"><i class="icon-share-alt"></i> Details</a>';
            }
        });
        // essential options, like the datasource
        var required_options = {
            "sAjaxSource": url,
            "aoColumns": columns
        };
        // allow passing any extra options, overriding the defaults below
        var extra_options = $el.data('options');
        if (!extra_options) {
            extra_options = {};
        }
        // sane options for any datatable
        var default_options = {
            "sDom": "<'row-fluid'<'span5'T><'span2'r><'span5 pull-right'f>><'row-fluid't><'row-fluid'<'span6'i><'span6 pull-right'p>><'row-fluid'<'span6 pull-right'l>>",
            "asStripeClasses": [],
            "bAutoWidth": false,
            "fnDrawCallback": function (oSettings) {
                // nothing
            },
            "oTableTools": {
                "sRowSelect": "multi",
                "sSwfPath": global.lizard.static_url + "ddsc_management/DataTables-1.9.4/extras/TableTools/swf/copy_csv_xls_pdf.swf",
                "fnRowDeselected": function (nodes) {
                    // disable any buttons operating on selected rows here
                    var $btns = $custom_buttons.find('.selection-only');
                    var self = this;
                    // can't use nodes.length here ...
                    var amount_selected = self.fnGetSelected().length;
                    if (amount_selected == 0) {
                        $btns.attr("disabled", "disabled");
                    }
                },
                "fnRowSelected": function (nodes) {
                    // enable any buttons operating on selected rows here
                    var $btns = $custom_buttons.find('.selection-only');
                    var self = this;
                    // can't use nodes.length here ...
                    var amount_selected = self.fnGetSelected().length;
                    if (amount_selected != 0) {
                        $btns.removeAttr("disabled");
                    }
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
        var options = $.extend({}, default_options, required_options, extra_options);
        var data_table = $el.dataTable(options);
        var oTT = TableTools.fnGetInstance(data_table.get()[0]);
        $container = $el.parents('.dataTables_wrapper');

        // add our custom buttons
        $custom_buttons = $('<div class="row-fluid custom-buttons" />');
        $container.append($custom_buttons);

        add_custom_buttons($custom_buttons, data_table, delete_url);
        fix_selection_on_page_change(data_table);
    });
}

function show_confirm_modal (header, message, continue_callback) {
    var $container = $('<div/>');
    var template_html = $('#modal-template').html();
    $container.html(template_html);
    var $modal = $container.find('.modal');
    $modal.appendTo($('body'));
    $container.remove();

    $modal.find('.modal-header-label').html(header);
    $modal.find('.modal-body p').html(message);
    $modal.find('.modal-continue').click(function (event) {
        if (typeof continue_callback !== 'undefined') {
            continue_callback(event);
        }
        $modal.modal('hide');
    });
    $modal.modal({
        show: true
    });

    // ensure element is properly destroyed
    // currently Twitter Bootstrap lacks a modal('destroy') method:
    // https://github.com/twitter/bootstrap/issues/5884
    $modal.on('hidden', function () {
        $(this).data('modal', null);
        $(this).remove();
    });
}

function create_inline_form_modal (header, app_label, model_name, field, form_url, submit_callback) {
    // wrap template in a container and extract .modal element
    var $container = $('<div>');
    var template_html = $('#modal-template').html();
    $container.html(template_html);
    var $modal = $container.find('.modal');
    $modal.appendTo($('body'));
    $container.remove();

    // update the header
    $modal.find('.modal-header-label').html(header);

    function continue_inline_form_modal (event) {
        $modal.find('.modal-body form').submit();
        // if (typeof submit_callback !== 'undefined') {
            // submit_callback(event);
        // }
        // $modal.modal('hide');
    }

    // retrieve the form and stuff it in the modal body
    $.get(form_url)
    .success(function (data) {
        $modal.find('.modal-body').html(data);
        $modal.find('.modal-continue').click(continue_inline_form_modal);
    })
    .error(function (data) {
        $modal.find('.modal-body').html('<p class="error">Error loading form.</p>');
    })
    .complete(function () {
        $modal.modal({
            show: true
        });

        // ensure element is properly destroyed
        // currently Twitter Bootstrap lacks a modal('destroy') method:
        // https://github.com/twitter/bootstrap/issues/5884
        $modal.on('hidden', function () {
            $(this).data('modal', null);
            $(this).remove();
        });
    });
}

function init_inline_forms () {
    $(document).on('click',
        'button[data-inline-add-app-label]',
        function (event) {
            var app_label = $(this).data('inline-add-app-label');
            var model_name = $(this).data('inline-add-model-name');
            var field = $(this).data('inline-add-field');
            var form_url = $(this).data('inline-add-form-url');
            create_inline_form_modal('hdr', app_label, model_name, field, form_url);
        }
    );
}

$(document).ready(function () {
    init_dynamic_forms();
    init_dynamic_links();
    init_inline_forms();
    init_data_tables();
});
}(this));