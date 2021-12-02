odoo.define('theme_prime.rte.summernote', function (require) {

require('web_editor.rte.summernote');
const core = require('web.core');

const _t = core._t;

const dom = $.summernote.core.dom;
const eventHandler = $.summernote.eventHandler;

const fn_attach = eventHandler.attach;
eventHandler.attach = function (oLayoutInfo, options) {
    fn_attach.call(this, oLayoutInfo, options);
    create_dblclick_feature('i.dri, span.dri', function () {
        eventHandler.modules.imageDialog.show(oLayoutInfo);
    });
    function create_dblclick_feature(selector, callback) {
        var show_tooltip = true;

        oLayoutInfo.editor().on("dblclick", selector, function (e) {
            var $target = $(e.target);
            if (!dom.isContentEditable($target)) {
                // Prevent edition of non editable parts
                return;
            }

            show_tooltip = false;
            callback();
            e.stopImmediatePropagation();
        });

        oLayoutInfo.editor().on("click", selector, function (e) {
            var $target = $(e.target);
            if (!dom.isContentEditable($target)) {
                // Prevent edition of non editable parts
                return;
            }

            show_tooltip = true;
            setTimeout(function () {
                // Do not show tooltip on double-click and if there is already one
                if (!show_tooltip || $target.attr('title') !== undefined) {
                    return;
                }
                $target.tooltip({title: _t('Double-click to edit'), trigger: 'manuel', container: 'body'}).tooltip('show');
                setTimeout(function () {
                    $target.tooltip('dispose');
                }, 800);
            }, 400);
        });
    }
};

});
