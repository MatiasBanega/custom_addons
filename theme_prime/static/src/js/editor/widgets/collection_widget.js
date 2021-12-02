odoo.define('theme_prime.widgets.collection_widget', function (require) {
'use strict';

const {_t, qweb} = require('web.core');
const AbstractWidget = require('theme_prime.widgets.abstract_widget');
const DialogWidgetRegistry = require('theme_prime.dialog_widgets_registry');
const SnippetConfigurator = require('theme_prime.dialog.snippet_configurator_dialog');
const {SortableMixins} = require('theme_prime.mixins');

let CollectionWidget = AbstractWidget.extend(SortableMixins, {

    template: 'collection_widget',

    xmlDependencies: AbstractWidget.prototype.xmlDependencies.concat(
        ['/theme_prime/static/src/xml/editor/widgets/collection_widget.xml']
    ),

    events: _.extend({}, AbstractWidget.prototype.events, {
        'click .d_add_collection': '_onClickAddCollection',
        'click .d_open_configrator': '_onClickOpenConfigurator',
        'click .d_remove_item': '_onRemoveCollectionClick',
    }),

    d_tab_info: {icon: 'fa fa-list', label: _t('Collections'), name: 'CollectionWidget'},
    d_attr: 'data-collection-params',

    start: function () {
        this._makeListSortable();
        this._togglePlaceHolder();
        return this._super.apply(this, arguments);
    },
    setWidgetState: function (data) {
        this.collections = data;
    },
    WidgetCurrentstate: function () {
        return {
            d_attr: 'data-collection-params',
            value: _.map(this.$('.d_collection_item'), item => {
                let $item = $(item);
                let attrValue = $item.attr('data-products');
                let widgetVal = attrValue ? JSON.parse(attrValue) : false;
                return {
                    data: widgetVal,
                    title: $item.find('#d_collection_title').val(),
                };
            }),
        };
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * Refresh list of products.
     *
     * @private
     */
    _togglePlaceHolder: function () {
        let items = !!this.$('.d_collection_item').length;
        this.trigger_up('widget_value_changed', {val: items});
        this.$('.d-snippet-config-placeholder').toggleClass('d-none', items);
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _onClickAddCollection: function () {
        this.$('.d_sortable_block').append(qweb.render('collection_item', {
            collection: {
                data: false,
            },
        }));
        this._togglePlaceHolder();
    },
    /**
     * @private
     * @param {Event} ev
     */
    _onRemoveCollectionClick: function (ev) {
        let $product = $(ev.currentTarget).closest('.d_collection_item');
        $product.remove();
        this._togglePlaceHolder();
    },
    /**
     * @private
     * @param {Event} ev
     */
    _onClickOpenConfigurator: function (ev) {
        let $target = $(ev.currentTarget);
        let id = _.uniqueId('d_id_');
        let $item = $target.closest('.d_collection_item');
        $item.attr('data-id', id);
        let attrValue = $item.attr('data-products');
        let widgetVal = attrValue ? JSON.parse(attrValue) : false;
        this.SnippetConfigurator = new SnippetConfigurator(this, {
            widgets: {ProductsWidget: widgetVal},
            size: 'large',
            title: _t('Product selector'),
        });
        this.SnippetConfigurator.on('d_final_pick', this, function (ev) {
            ev.stopPropagation();
            this.$('.d_collection_item[data-id=' + id + ']').attr('data-products', JSON.stringify(ev.data.ProductsWidget.value));
        });
        this.SnippetConfigurator.open();
    },
});

DialogWidgetRegistry.add('CollectionWidget', CollectionWidget);

return CollectionWidget;
});
