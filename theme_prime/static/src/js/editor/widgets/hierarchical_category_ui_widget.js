odoo.define('theme_prime.widgets.hierarchical_category_ui_widget', function (require) {
'use strict';

const {_t} = require('web.core');
const AbstractUIWidget = require('theme_prime.widgets.abstract_ui_widget');
const hierarchicalCategoryStyleRegistry = require('theme_prime.hierarchical_category_styles');
const DialogWidgetRegistry = require('theme_prime.dialog_widgets_registry');

let hierarchicalCategoryUIWidget = AbstractUIWidget.extend({

    xmlDependencies: AbstractUIWidget.prototype.xmlDependencies.concat(['/theme_prime/static/src/xml/frontend/hierarchical_category_templates.xml']),

    d_tab_info: {icon: 'fa fa-paint-brush', label: _t('Category UI'), name: 'hierarchicalCategoryUIWidget'},
    d_attr: 'data-hierarchical-category-style',
    drAllTemplates: hierarchicalCategoryStyleRegistry.keys(),
    defaultTemplateStyle: 's_tp_hierarchical_category_style_1',
    templateTargetNodeAttr: 'hierarchicalCategoryStyle',
    PreviewTemplateAttr: 'category',
    templatePriviewClasses: 'mx-auto w-50',

    /**
     * @private
     */
    _getDemoData: function () {
        return {
            parentCategory: {category_lable_info: {color: "green", id: 1, name: "22 % OFF"}, id: 1, cover_image: '/theme_prime/static/src/img/tp_category_bg.jpg', website_url: '/', image_url: '/theme_prime/static/src/img/category_1.png', name: _t("Parent category")},
            childCategories: [{id: 2, cover_image: '/theme_prime/static/src/img/tp_category_bg.jpg', website_url: '/', image_url: '/theme_prime/static/src/img/category_1.png', name: _t("Child category 1")}
                , {category_lable_info: {color: "blue", id: 1, name: "22 % OFF"}, id: 2, cover_image: '/theme_prime/static/src/img/tp_category_bg.jpg', website_url: '/', image_url: '/theme_prime/static/src/img/category_1.png', name: _t("Child category 2")}
                , {id: 2, cover_image: '/theme_prime/static/src/img/tp_category_bg.jpg', website_url: '/', image_url: '/theme_prime/static/src/img/category_1.png', name: _t("Child category 3")}]
        };
    },
});

DialogWidgetRegistry.add('hierarchicalCategoryUIWidget', hierarchicalCategoryUIWidget);

return hierarchicalCategoryUIWidget;
});
