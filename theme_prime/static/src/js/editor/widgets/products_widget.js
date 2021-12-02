odoo.define('theme_prime.widgets.products_widget', function (require) {
'use strict';

const {_t, qweb} = require('web.core');
const AbstractWidget = require('theme_prime.widgets.abstract_widget');
const Select2Dialog = require('theme_prime.dialog.product_selector');
const DomainBuilder = require('theme_prime.domain_builder').DomainBuilder;
const DialogWidgetRegistry = require('theme_prime.dialog_widgets_registry');
const {SortableMixins, ProductsMixin} = require('theme_prime.mixins');

let ProductsWidget = AbstractWidget.extend(SortableMixins, ProductsMixin, {

    template: 'theme_prime.products_widget',

    xmlDependencies: AbstractWidget.prototype.xmlDependencies.concat(['/theme_prime/static/src/xml/editor/widgets/products_widget.xml']),

    events: _.extend({}, AbstractWidget.prototype.events, {
        'click .d_add_product': '_onAddProductClick',
        'click .d_remove_item': '_onRemoveProductClick',
        'click .d_selection_type_btn': '_onSwitchSelectionTypeClick',
    }),

    d_tab_info: {
        icon: 'fa fa-cubes',
        label: _t('Products'),
        name: 'ProductsWidget',
    },

    d_attr: 'data-products-params',

    /**
     * @override
     * @returns {Promise}
     */
    willStart: function () {
        let defs = [this._super.apply(this, arguments)];
        if (this.productIDs.length && this.activeSelectionType === 'manual') {
            defs.push(this._fetchProductsData(this.productIDs).then(data => {
                this._setProducts(data);
            }));
        }
        return Promise.all(defs);
    },
    /**
     * @override
     * @returns {Promise}
     */
    start: function () {
        this._makeListSortable();
        this._togglePlaceHolder();
        if (!this.noSwicher) {
            this._appendDomainBuilder();
        }
        return this._super.apply(this, arguments);
    },

    //--------------------------------------------------------------------------
    // Getters
    //--------------------------------------------------------------------------

    /**
     * @override
     * @returns {Array} list of selected products / domain with it state
     */
    WidgetCurrentstate: function () {
        let result = {
            selectionType: this.activeSelectionType,
        };
        switch (this.activeSelectionType) {
            case 'manual':
                result['productIDs'] = this._getProductIDs();
                break;
            case 'advance':
                result['domain_params'] = this.DomainBuilder.getDomain();
                break;
        }
        return {
            value: result,
            d_attr: this.d_attr
        };
    },
    /**
     * @constructor
     * @param {Object} options: useful parameters such as productIDs, domain etc.
     */
    setWidgetState: function (options) {
        options = options || {};
        this.productIDs = options.productIDs || [];
        this.domain_params = options.domain_params || false;
        this.products = [];
        this.activeSelectionType = options.selectionType || 'manual';
        this.noSwicher = options.noSwicher || false;
        this.select2Limit = options.select2Limit || 0;
        this._setSelectionType();
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * Refresh list of products.
     *
     * @private
     */
    _refreshProductsList: function () {
        let $productList = this.$('.d_sortable_block');
        $productList.empty();
        if (this.products.length) {
            $productList.append(qweb.render('theme_prime.products_list', {products: this.products}));
        }
        this._togglePlaceHolder();
    },
    /**
     * @private
     */
    _appendDomainBuilder: function () {
        this.DomainBuilder = new DomainBuilder(this, this.domain_params);
        this.DomainBuilder.appendTo(this.$('.d_advance_selection_body'));
    },
    /**
     * @private
     * @returns {Array} productIDs
     */
    _getProductIDs: function () {
        return _.map(this.$('.d_list_item'), item => {
            return $(item).data('productId');
        });
    },
    /**
     * @private
     */
    _getSelectionTypes: function () {
        return {
            manual: {label: _t('Manual Selection'), type: 'manual'},
            advance: {label: _t('Advance Selection'), type: 'advance'}
        };
    },
    /**
     * Set Products [ For more info contact KIG :) ]
     *
     * @param {Array} data
     * @private
     */
    _setProducts: function (data) {
        let products = _.map(this.productIDs, function (product) {
            return _.findWhere(data.products, {id: product});
        });
        this.products = _.compact(products); // compact is mandatory in case product is not available now.
        this.productIDs = _.map(this.products, function (product) {
            return product.id;
        });
    },
    /**
     * @private
     */
    _setSelectionType: function () {
        this.SelectionBtns = _.map(this._getSelectionTypes(), r => {
            r['active'] = r.type === this.activeSelectionType;
            return r;
        });
    },
    /**
     * @private
     */
    _togglePlaceHolder: function () {
        let items = this.$('.d_list_item').length;
        this.trigger_up('widget_value_changed', {val: this.activeSelectionType === 'advance' ? true : items});
        this.$('.d-snippet-config-placeholder').toggleClass('d-none', !!items);
        this.$('.d_product_selector_title').toggleClass('d-none', !items);
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _onAddProductClick: function () {
        let currentSelectedProducts = this._getProductIDs();
        let ProductDialog = new Select2Dialog(this, {
            multiSelect: true,
            records: this.products,
            recordsIDs: currentSelectedProducts,
            routePath: '/theme_prime/get_product_by_name',
            fieldLabel: _t("Select Product"),
            dropdownTemplate: 'd_select2_products_dropdown',
            select2Limit: this.select2Limit,
        });
        ProductDialog.on('d_product_pick', this, function (ev) {
            let productsToAdd = ev.data.result;
            if (productsToAdd) {
                // Don't fetch already fetched products. But someday we will remove it.
                let productsToFetch = _.without(productsToAdd, currentSelectedProducts);
                this._fetchProductsData(productsToFetch).then(data => {
                    let products = _.union(data.products, this.products);
                    this.products = _.map(productsToAdd, function (product) {
                        return _.findWhere(products, {id: product});
                    });
                    this._refreshProductsList();
                    this.productIDs = this._getProductIDs();
                });
            } else {
                this.products = [];
                this.productIDs = [];
                this._refreshProductsList();
            }
        });
        ProductDialog.open();
    },
    /**
     * @private
     * @param {Event} ev
     */
    _onRemoveProductClick: function (ev) {
        let $product = $(ev.currentTarget).closest('.d_list_item');
        $product.remove();
        this.products = _.without(this.products, _.findWhere(this.products, {id: parseInt($product.attr('data-product-id'), 10)}));
        this.productIDs = this._getProductIDs();
        this._togglePlaceHolder();
    },
    /**
     * @private
     * @param {Event} ev
     */
    _onSwitchSelectionTypeClick: function (ev) {
        let $target = $(ev.currentTarget);
        this.activeSelectionType = $target.data('type');
        this.$('.d_body_content').addClass('d-none');
        this.$('.d_' + $target.data('type') + '_selection_body').removeClass('d-none');
        this._togglePlaceHolder();
    },
});

DialogWidgetRegistry.add('ProductsWidget', ProductsWidget);

return ProductsWidget;

});
