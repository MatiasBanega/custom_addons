odoo.define('theme_prime.dialog.snippet_configurator_dialog', function (require) {
'use strict';

var core = require('web.core');
var weWidgets = require('web_editor.widget');

var DialogWidgetRegistry = require('theme_prime.dialog_widgets_registry');

var WeDialog = weWidgets.Dialog;

var _t = core._t;

return WeDialog.extend({

    template: 'theme_prime.snippet_configurator_dialog',

    xmlDependencies: WeDialog.prototype.xmlDependencies.concat(['/theme_prime/static/src/xml/editor/dialogs/snippet_configurator_dialog.xml']),
    custom_events: _.extend({}, WeDialog.prototype.custom_events, {
        widget_value_changed: '_onValueChanged',
    }),
    events: _.extend({}, WeDialog.prototype.events || {}, {
        'click .tp-save-btn': '_onSaveDialog',
        'click .tp-close-btn': 'close',
    }),

    /**
     * @constructor
     */
    init: function (parent, options) {
        this._super(parent, _.extend({
            title: options.title || _t('Configurator'),
            size: options.size || 'extra-large',
            technical: false,
            renderHeader: false,
            renderFooter: false,
            dialogClass: 'd-snippet-config-dialog p-0'
        } || {}));
        this.tabs = [];
        this.widgets = options.widgets;
        this._initializeWidgets();
    },
    /**
     * @override
     * @returns {Promise}
     */
    start: function () {
        this.$modal.addClass('droggol_technical_modal');
        this._appendWidgets();
        this.$modal.find('.modal-dialog').addClass('modal-dialog-centered');
        return this._super.apply(this, arguments);
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _appendWidgets: function () {
        var self = this;
        _.each(this.widgets, function (val, key) {
            if (self[key]) {
                self[key].appendTo(self.$('#' + key)).then(function () {
                    self._initTips();
                });
            }
        });
    },
    /**
     * init tooltips
     *
     * @private
     */
    _initTips: function () {
        this.$('[data-toggle="tooltip"]').tooltip();
    },
    /**
     * @private
     */
    _initializeWidgets: function () {
        var self = this;
        _.each(this.widgets, function (val, key) {
            var widget = DialogWidgetRegistry.get(key);
            self[key] = new widget(self, val);
            self.tabs.push(self[key].d_tab_info);
        });
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _onSaveDialog: function () {
        var self = this;
        var result = {};
        _.each(this.widgets, function (val, key) {
            if (self[key]) {
                result[key] = self[key].WidgetCurrentstate();
            }
        });
        this.trigger_up('d_final_pick', result);
        this.close();
    },
    /**
     * @private
     */
    _onValueChanged: function (ev) {
        this.$('.tp-save-btn').prop('disabled', !ev.data.val);
    },
});

});
