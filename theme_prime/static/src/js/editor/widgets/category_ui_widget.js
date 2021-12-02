odoo.define('theme_prime.widgets.category_ui_widget', function (require) {
'use strict';

const {_t} = require('web.core');
const AbstractUIWidget = require('theme_prime.widgets.abstract_ui_widget');
const FilterRegistry = require('theme_prime.category_filter_registry');
const DialogWidgetRegistry = require('theme_prime.dialog_widgets_registry');

let CategoryUIWidget = AbstractUIWidget.extend({

    xmlDependencies: AbstractUIWidget.prototype.xmlDependencies.concat(['/theme_prime/static/src/xml/frontend/category_filters.xml']),

    d_tab_info: {icon: 'fa fa-paint-brush', label: _t('Category UI'), name: 'CategoryUIWidget'},
    d_attr: 'data-category-filter-style',
    drAllTemplates: FilterRegistry.keys(),
    defaultTemplateStyle: 'd_category_filter_style_1',
    templateTargetNodeAttr: 'categoryFilterStyle',
    PreviewTemplateAttr: 'categories',

    /**
     * @private
     */
    _getDemoData: function () {
        return [{id: 1, name: _t("All")}, {id: 2, name: _t("Men")}, {id: 3, name: _t("Women")}, {id: 4, name: _t("Kids")}, {id: 5, name: _t("Accessories")}];
    },
});

DialogWidgetRegistry.add('CategoryUIWidget', CategoryUIWidget);

return CategoryUIWidget;
});
