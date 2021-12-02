odoo.define('theme_prime.widgets.abstract_ui_widget', function (require) {
'use strict';

const {qweb} = require('web.core');
const AbstractWidget = require('theme_prime.widgets.abstract_widget');

return AbstractWidget.extend({
    template: 'theme_prime.abstract_ui_widget',

    xmlDependencies: AbstractWidget.prototype.xmlDependencies.concat(['/theme_prime/static/src/xml/editor/widgets/abstract_ui_widget.xml']),

    events: _.extend({}, AbstractWidget.prototype.events, {
        'change #tp_style_select': '_onChangeFilterStyle',
    }),

    drAllTemplates: false,
    templateTargetNodeAttr: false,
    defaultTemplateStyle: false,
    templateVariable: false,
    defaultWidgetTemplate: 'tp_abstract_ui_widget',
    templatePriviewClasses: '',

    /**
     * @override
     */
    start: function () {
        this._refreshPreview();
        return this._super.apply(this, arguments);
    },
    /**
     * @override
     */
    setWidgetState: function (options) {
        this[this.templateTargetNodeAttr] = options[this.templateTargetNodeAttr] || this.defaultTemplateStyle;
    },
    /**
     * @override
     */
    WidgetCurrentstate: function () {
        let val = {};
        val[this.templateTargetNodeAttr] = this.$('#tp_style_select').val();
        return {value: val, d_attr: this.d_attr};
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _getDemoData: function () {},
    /**
     * Refresh preview
     *
     * @private
     */
    _refreshPreview: function () {
        let val = {widget: this};
        val[this.PreviewTemplateAttr] = this._getDemoData();
        this.$('.tp-abstract-ui-preview').empty().append(qweb.render(this.defaultWidgetTemplate, val));
    },
    // Handlers
    _onChangeFilterStyle: function (ev) {
        this[this.templateTargetNodeAttr] = $(ev.currentTarget).val();
        this._refreshPreview();
    },
});
});
