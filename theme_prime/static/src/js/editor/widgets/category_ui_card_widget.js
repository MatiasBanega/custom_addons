odoo.define('theme_prime.widgets.category_ui_card_widget', function (require) {
'use strict';

const {_t} = require('web.core');
const AbstractUIWidget = require('theme_prime.widgets.abstract_ui_widget');
const categoryUiCardStyleRegistry = require('theme_prime.category_ui_card_widget_styles');
const DialogWidgetRegistry = require('theme_prime.dialog_widgets_registry');

let categoryUiCardWidget = AbstractUIWidget.extend({

    xmlDependencies: AbstractUIWidget.prototype.xmlDependencies.concat(['/theme_prime/static/src/xml/frontend/s_category.xml']),

    d_tab_info: {icon: 'fa fa-paint-brush', label: _t('Category UI'), name: 'categoryUiCardWidget'},
    d_attr: 'data-category-style',
    drAllTemplates: categoryUiCardStyleRegistry.keys(),
    defaultTemplateStyle: 's_tp_category_style_1',
    templateTargetNodeAttr: 'categoryStyle',
    PreviewTemplateAttr: 'category',
    templatePriviewClasses: 'mx-auto w-75',

    /**
     * @private
     */
    _getDemoData: function () {
        return {cover_image: '/theme_prime/static/src/img/tp_category_bg.jpg', count: 15, website_url: '/', image_url: '/theme_prime/static/src/img/category_1.png', name: _t("Category")};
    },
});

DialogWidgetRegistry.add('categoryUiCardWidget', categoryUiCardWidget);

return categoryUiCardWidget;
});
