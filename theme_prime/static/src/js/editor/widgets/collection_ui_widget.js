odoo.define('theme_prime.widgets.collection_ui_widget', function (require) {
'use strict';

const {_t} = require('web.core');
const AbstractUIWidget = require('theme_prime.widgets.abstract_ui_widget');
const CollectionStyleRegistry = require('theme_prime.collection_style_registry');
const DialogWidgetRegistry = require('theme_prime.dialog_widgets_registry');


let CollectionUIWidget = AbstractUIWidget.extend({

    xmlDependencies: AbstractUIWidget.prototype.xmlDependencies.concat(['/theme_prime/static/src/xml/frontend/card_collection.xml']),

    d_tab_info: {icon: 'fa fa-paint-brush', label: _t('Collections UI'), name: 'CollectionUIWidget'},
    d_attr: 'data-collection-style',
    drAllTemplates: CollectionStyleRegistry.keys(),
    defaultTemplateStyle: 'd_card_collection_style_1',
    templateTargetNodeAttr: 'SelectedStyle',
    PreviewTemplateAttr: 'collection',
    templatePriviewClasses: 'mx-auto w-75',

    /**
     * @private
     */
    _getDemoData: function () {
        return {
            title: _t("New Arrivals"),
            products: _.map([1, 2, 3], function () {
                return {website_url: '#', img_medium: '/theme_prime/static/src/img/s_config_data.png', name: 'Product Name', price: '$ 13.00', has_discounted_price: true, list_price: '$ 22.10'};
            }),
        };
    },
});

DialogWidgetRegistry.add('CollectionUIWidget', CollectionUIWidget);

return CollectionUIWidget;
});
