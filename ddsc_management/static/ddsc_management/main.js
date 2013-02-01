(function (global) {

/**
 * Finds the element #{target} in data and replaces the current element
 * #{target} in the DOM with it.
 */
function dom_partial_replace (target, html) {
    // root elements with an id can't be found without wrapping first
    // (for some reason)
    var $wrapped = $('<div>' + html + '</div>');
    var $new_el = $wrapped.find('#' + target);
    var $old_el = $('#' + target);
    // Replace the old element containing the data with the
    // new one.
    // .replaceWith() internally calls .remove(), which
    // should properly unbind all event handlers.
    $old_el.replaceWith($new_el);
    // remove the wrapper as well
    $wrapped.remove();
}

/**
 * Replaces the element #{target} contents in the DOM with passed data.
 */
function dom_replace (target_id, html) {
    var $target = $('#' + target_id);
    // Replace the old element containing the data with the
    // new one.
    // .remove(), should properly unbind all event handlers.
    $target.children().remove();
    $target.html(html);
}


/**
 * Replaces the element #{target} in the DOM with passed data.
 */
function dom_replace_with (target, html) {
    var $target = $('#' + target);
    // Replace the old element containing the data with the
    // new one.
    // .remove(), should properly unbind all event handlers.
    $target.replaceWith(html);
}

$.fn.dynamic_load = function (url, params) {
    var $target = this;
    if (typeof params === 'undefined') {
        params = {};
    }
    // grep the data asynchronously
    $.get(url, params)
    .done(function (data, textStatus, jqXHR) {
        // stuff the resulting data in the target element
        // .remove(), should properly unbind all event handlers
        // not sure if $.empty() does this
        $target.children().remove();
        $target.html(data.html);
    })
    .fail(function (jqXHR, textStatus, errorThrown) {
        $target.children().remove();
        $target.html('<p class="error">Fout bij het laden van het formulier.</p>');
    });
};

/**
 * Detect all a.dynamic-link elements and make them partially replace
 * DOM fragments.
 */
function init_dynamic_links () {
    $(document).on('click',
        'a.dynamic-link',
        function (event) {
            // cancel the default click handler
            event.preventDefault();
            // find out where to load the resulting data
            var $el = $(this);
            var target = $el.data('target');
            if (!target) {
                console.error(
                    'No target id set, so can not properly determine target element.'
                );
                return;
            }
            // determine URL to be loaded
            var url = $el.attr('href');
            // grep the data asynchronously
            $.get(url)
            .done(function (data, textStatus, jqXHR) {
                // HACK to support dynamic forms opened via .dynamic-link
                // TODO remove me
                if (data.html) {
                    dom_replace(target, data.html);
                    return;
                }
                // stuff the resulting data in the target element
                dom_partial_replace(target, data);
            })
            .fail(function (jqXHR, textStatus, errorThrown) {
                // enforce a full screen refresh
                window.location = url
            });
        }
    );
}

/**
 * Detect all .dynamic-form elements, and add a custom submit
 * handler for them.
 */
function init_dynamic_forms () {
    function dynamic_submit (event, extraParameters) {
        // cancel the default submit handler
        event.preventDefault();
        // find out where to load the resulting data
        var $form = $(this);
        var target = $form.data('target');
        if (!target) {
            target = $form.attr('id');
        }
        if (!target) {
            console.error(
                'No id or target id set, so can not properly determine target element.'
            );
            return;
        }
        // post the form to the server
        $.post(
            $form.attr('action'),
            $form.serialize()
        )
        .done(function (data, textStatus, jqXHR) {
            // display the resulting html (might be the form again
            // if it is invalid)
            dom_replace_with(target, data.html);
            // when triggered via a custom event trigger, call the optional
            // callback
            if (data.success) {
                if (typeof extraParameters !== 'undefined') {
                    if (extraParameters.success_callback) {
                        extraParameters.success_callback(data);
                    }
                }
            }
        })
        .fail(function (jqXHR, textStatus, errorThrown) {
            // show an error message
            dom_replace_with(target, '<p class="error">Fout bij het laden van formulier.</p>');
        });
    }

    // listen to all submit events on the document
    // and select the ones which have .dynamic-form set
    $(document).on('submit',
        'form.dynamic-form',
        dynamic_submit
    );
}

/**
 * Add some extra buttons to a DataTable, like the "delete" button.
 */
function add_custom_buttons ($table, $container, data_table) {
    var delete_url = $table.data('delete-url');
    if (delete_url) {
        var $delete = $('<button class="btn btn-danger selection-only" disabled="disabled"><i class="icon-trash"></i> Verwijder geselecteerde item(s)</button>');
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
                    // define what happens when the user clicks "continue"
                    function continue_callback (event) {
                        $.post(
                            delete_url,
                            {
                                pks: selected
                            }
                        )
                        .done(function (data, textStatus, jqXHR) {
                            data_table.fnReloadAjax();
                            // would be nicer if we can retain the selected page here
                            // $.each(data.deleted, function (idx) {
                                // var pk = this.pk;
                                // alert(pk);
                                // //data_table.fnDeleteRow();
                            // });
                        })
                        .fail(function (jqXHR, textStatus, errorThrown) {
                            alert('Fout bij het verwijderen van item(s): ' + jqXHR.status + ' ' + jqXHR.statusText);
                        });
                    }
                    // open the modal
                    show_confirm_modal(
                        "Zeker?",
                        "Weet u zeker dat u de item(s) met ID = " + selected + " wilt verwijderen?",
                        continue_callback
                    );
                }
            }
        });
        $('<div class="span12"/>')
            .wrapInner($delete)
            .appendTo($container);
    }
}

/**
 * Fix DataTables so it deselects everything when switching
 * a page. Call once for each initialized DataTable.
 */
function fix_selection_on_page_change (data_table) {
    data_table.on('page', function (event) {
        var oTT = TableTools.fnGetInstance(data_table.get()[0]);
        oTT.fnSelectNone();
    });
}

/**
 * Example of how to hook into a custom JSON data source
 * with DataTables.
 */
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

/**
 * Scan all .data-table elements on the page and make a DataTable out of them.
 * @see http://datatables.net/
 */
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
        var detail_target = $el.data('detail-target');
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
        // columns.push({
            // "aTargets": ["details_url"],
            // "sName": "details_url",
            // "sTitle": "Acties",
            // "bSortable": false,
            // "mRender": function (data, type, full) {
                // return '<a class="btn btn-mini dynamic-link no-select" href="'+ data +'" data-target="detail-view"><i class="icon-share-alt"></i> Details</a>';
            // }
        // });
        columns.push({
            "aTargets": ["pk"],
            "sName": "pk",
            "sTitle": "Acties",
            "bSortable": false,
            "mRender": function (data, type, full) {
                return '<button class="btn btn-mini" data-pk="'+ data +'" data-detail-target="' + detail_target + '"><i class="icon-share-alt"></i> Details</button>';
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
            "sPaginationType": "bootstrap",
            "fnDrawCallback": function (oSettings) {
                // nothing yet
            },
            "oTableTools": {
                "sRowSelect": "multi",
                "sSwfPath": global.lizard.static_url + "ddsc_management/DataTables/extras/TableTools/swf/copy_csv_xls_pdf.swf",
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

        add_custom_buttons($el, $custom_buttons, data_table);
        fix_selection_on_page_change(data_table);
    });
}

/**
 * Spawn and return an unopened Bootstrap Modal:
 * @see http://twitter.github.com/bootstrap/javascript.html#modals
 */
function create_modal (header) {
    // wrap template in a container and extract .modal element
    var $container = $('<div>');
    var template_html = $('#modal-template').html();
    $container.html(template_html);
    var $modal = $container.find('.modal');
    $modal.appendTo($('body'));
    $container.remove();

    // update the header when defined
    if (typeof header !== 'undefined') {
        $modal.find('.modal-header-label').html(header);
    }

    // dont open the modal yet
    $modal.modal({
        show: false
    });

    // ensure modal is properly destroyed
    // currently Twitter Bootstrap lacks a modal('destroy') method:
    // https://github.com/twitter/bootstrap/issues/5884
    $modal.on('hidden', function () {
        $(this).data('modal', null);
        $(this).remove();
    });

    return $modal;
}

/**
 * Shows a simple modal, which a header and a message. Calls the optional
 * continue_callback, when the user clicks "continue".
 * This happens before closing the modal.
 */
function show_confirm_modal (header, message, continue_callback) {
    var $modal = create_modal(header);

    $modal.find('.modal-body').html(message);
    $modal.find('.modal-continue').click(function (event) {
        if (typeof continue_callback !== 'undefined') {
            continue_callback(event);
        }
        $modal.modal('hide');
    });
    $modal.modal('show');
}

/**
 * Show a modal with a lazy-loaded form. When form is succesfully submitted,
 * calls arg_success_callback with the server data passed on.
 */
function show_inline_add_modal (header, model_name, field, related_model_name, form_url, arg_success_callback) {
    var $modal = create_modal(header);

    // submit the inner form when clicking on "continue"
    function continue_click (event) {
        var $form = $modal.find('.modal-body form');
        // close the modal on success
        function success_callback (data) {
            if (typeof arg_success_callback !== 'undefined') {
                arg_success_callback(data);
            }
            $modal.modal('hide');
        }
        $form.trigger('submit', {'success_callback': success_callback});
    }

    // retrieve the form and stuff it in the modal body
    $.get(
        form_url,
        {
            // this hide the default submit button,
            // we use the 'continue' button for submitting
            for_modal: 'True'
        }
    )
    .done(function (data, textStatus, jqXHR) {
        $modal.find('.modal-body').html(data.html);
        $modal.find('.modal-continue').click(continue_click);
    })
    .fail(function (jqXHR, textStatus, errorThrown) {
        $modal.find('.modal-body').html('<p class="error">Fout bij het laden van formulier.</p>');
    })
    .always(function () {
        $modal.modal('show');
    });
}

/**
 * Augments all form fields which derive from SelectWithInlineFormPopup
 * as defined in forms.py.
 */
function init_inline_add () {
    $(document).on('click',
        'button[data-inline-add-form-url]',
        function (event) {
            // get the model for which we need to generate a form
            var $button = $(this);
            var model_name = $button.data('inline-add-model-name');
            var field = $button.data('inline-add-field');
            var related_model_name = $button.data('inline-add-related-model-name');
            var form_url = $button.data('inline-add-form-url');

            // add an <option> to the nearest <select> when the modal closes
            function success_callback (data) {
                var $select = $button.siblings('select');
                // add a new option
                $('<option>')
                .attr('value', data.pk)
                .text(data.name)
                .appendTo($select);
                // immediately select it
                $select.val(data.pk);
            }

            // open a modal
            show_inline_add_modal('Voeg ' + related_model_name + ' toe', model_name, field, related_model_name, form_url, success_callback);
        }
    );
}

function init_add_edit_detail_panels () {
    $('.add-edit-detail-panel').each(function (idx) {
        var $el = $(this);

        // wrap template in a container and extract .modal element
        var $container = $('<div>');
        var template_html = $('#add-edit-detail-template').html();
        $container.html(template_html);
        var $content = $container.find('.content');
        var $buttons = $container.find('.buttons');
        $container.children().appendTo($el);
        $container.remove();

        // fetch urls
        var detail_url = $el.data('detail-url');
        var add_form_url = $el.data('add-form-url');
        var edit_form_url = $el.data('edit-form-url');

        // fetch buttons
        var $add = $buttons.find('.add');
        var $edit = $buttons.find('.edit');
        var $cancel = $buttons.find('.cancel');

        var current_pk = null;
        var current_mode = null;

        function set_pk (pk) {
            current_pk = pk;
            set_mode('detail');
        }

        function set_mode (mode) {
            if (mode == 'detail') {
                $content.dynamic_load(detail_url, {pk: current_pk});
                $add.hide();
                $edit.show();
                $cancel.show();
            }
            else if (mode == 'add') {
                $content.dynamic_load(add_form_url);
                $add.hide();
                $edit.hide();
                $cancel.show();
            }
            else if (mode == 'edit') {
                $content.dynamic_load(edit_form_url, {pk: current_pk});
                $add.hide();
                $edit.hide();
                $cancel.show();
            }
            else if (mode == 'initial') {
                $content.html('Geen item geselecteerd.');
                $add.show();
                $edit.hide();
                $cancel.hide();
            }

            current_mode = mode;
        }

        // attach click handlers
        $add.click(function (event) {
            set_mode('add');
        });
        $edit.click(function (event) {
            set_mode('edit');
        });
        $cancel.click(function (event) {
            if (current_mode == 'edit') {
                set_mode('detail');
            }
            else if (current_mode == 'add' || current_mode == 'detail') {
                set_mode('initial');
            }
        });

        // allow other elements to change the pk
        $el.on('set_pk', function (event, pk) {
            set_pk(pk);
        });

        // set initial state
        set_mode('initial');
    });

    $(document).on('click',
        'button[data-detail-target]',
        function (event) {
            var target_selector = $(this).data('detail-target');
            var pk = $(this).data('pk');
            var $target = $(target_selector);
            $target.trigger('set_pk', pk);
        }
    );
}

function show_tree_modal (field, tree_url, arg_success_callback) {
    var $modal = create_modal('Lokaties');

    // retrieve the form and stuff it in the modal body
    var $tree = $('<div>');
    $modal.find('.modal-body').children().remove()
    $modal.find('.modal-body').append($tree);

    $tree.jstree({
        json_data: {
            ajax: {
                url: tree_url,
                data: function (n) {
                    if (n.attr) {
                        return {parent_pk: n.data('pk')};
                    }
                    else {
                        return {};
                    }
                },
                error: function (e) {
                    console.error(e);
                }
            }
        },
        ui: {select_multiple_modifier: false},
        core: {html_titles: true, load_open: true},
        plugins: ["themes", "json_data", "ui"]
    });

    // pass selected item PK back when clicking continue
    function continue_click (event) {
        var $form = $modal.find('.modal-body form');
        var $selected_item = $tree.jstree('get_selected');
        var data = {
            pk: $selected_item.data('pk')
        };
        if (typeof arg_success_callback !== 'undefined') {
            arg_success_callback(data);
        }
        // close the modal on success
        $modal.modal('hide');
    }

    $modal.find('.modal-continue').click(continue_click);
    $modal.modal('show');
}

function init_tree_modal () {
    $(document).on('click',
        'button[data-tree-popup="true"]',
        function (event) {
            // get the model for which we need to generate a form
            var $button = $(this);
            var field = $button.data('field');
            var tree_url = $button.data('tree-url');

            // add an <option> to the nearest <select> when the modal closes
            function success_callback (data) {
                var $input = $button.siblings('input');
                $input.val(data.pk);
            }

            // open a modal
            show_tree_modal(field, tree_url, success_callback);
        }
    );
}

$(document).ready(function () {
    init_dynamic_forms();
    init_dynamic_links();

    init_inline_add();
    init_tree_modal();
    init_data_tables();
    init_add_edit_detail_panels();
});
}(this));