odoo.define('theme_prime.mixins', function (require) {
"use strict";

let wUtils = require('website.utils');
let {qweb, _t} = require('web.core');
let DroggolNotification = require('theme_prime.notification.manger');
let ConfirmationDialog = require('theme_prime.cart_confirmation_dialog');
const {CartSidebar} = require('theme_prime.cart_sidebar');


let DroggolUtils = {
    _getDomainWithWebsite: function (domain) {
        return domain.concat(wUtils.websiteDomain(this));
    },
};

let SortableMixins = {
    /**
     * @private
     */
    _makeListSortable: function () {
        this.$('.d_sortable_block').nestedSortable({
            listType: 'ul',
            protectRoot: true,
            handle: '.d_sortable_item_handel',
            items: 'li',
            toleranceElement: '> .row',
            forcePlaceholderSize: true,
            opacity: 0.6,
            tolerance: 'pointer',
            placeholder: 'd_drag_placeholder',
            maxLevels: 0,
            expression: '()(.+)',
        });
    },
};

let cartMixin = {
    /**
    * @private
    */
    _addProductToCart: function (cartInfo, QuickViewDialog) {
        // Do not add variant for default flow
        let isCustomFlow = _.contains(['side_cart', 'dialog', 'notification'], odoo.dr_theme_config.cart_flow || 'default');
        let dialogOptions = {mini: true, size: 'small', add_if_single_variant: isCustomFlow};
        dialogOptions['variantID'] = cartInfo.productID;
        this.QuickViewDialog = new QuickViewDialog(this, dialogOptions).open();
        return this.QuickViewDialog;
    },
    /**
    * @private
    */
    _getCartParams: function (ev) {
        return {productID: parseInt($(ev.currentTarget).attr('data-product-product-id')), qty: 1};
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param  {Event} ev
     */
    onAddToCartClick: function (ev, QuickViewDialog) {
        this._addProductToCart(this._getCartParams(ev), QuickViewDialog);
    },
};

let ProductCarouselMixins = {
    _updateIDs: function ($target) {
        // carousel with same id fuck everything
        let newID = _.uniqueId('d_carousel_');
        $target.find('#o-carousel-product').addClass('d_shop_product_details_carousel');
        $target.find('#o-carousel-product').attr('id', newID);
        $target.find('[href="#o-carousel-product"]').attr('href', '#' + newID);
        $target.find('[data-target="#o-carousel-product"]').attr('data-target', '#' + newID);
    },
};

let CategoryWidgetMixins = {
    /**
     * @private
     * @returns {Array} categoryIDs
     */
    _getCategoryIDs: function () {
        return _.map(this.$('.d_category_item'), item => {
            return parseInt($(item).attr('data-category-id'), 10);
        });
    },
    /**
     * @private
     * @returns {Array} categoryIDs
     */
    _fetchCategories: function (categoryIDs) {
        return this._rpc({
            model: 'product.public.category',
            method: 'search_read',
            fields: ['id', 'name', 'display_name'],
            domain: this._getDomainWithWebsite([['id', 'in', categoryIDs]]),
        });
    },
};
let CategoryMixins = {
    _getParsedSortBy: function (val) {
        let order = {price_asc: 'list_price asc', price_desc: 'list_price desc', name_asc: 'name asc', name_desc: 'name desc', newest_to_oldest: 'create_date desc'};
        return order[val];
    },
    /**
     * @private
     * @returns {Integer} categoryID
     */
    _fetchProductsByCategory: function (categoryID, includesChild, order, limit, fields) {
        var operator = '=';
        if (includesChild) {
            operator = 'child_of';
        }
        // this._rpc will work for now next version may includes service mixins
        return this._rpc({
            route: '/theme_prime/get_products_by_category',
            params: {
                domain: [['public_categ_ids', operator, categoryID]],
                fields: fields,
                options: {order: order, limit: limit}
            },
        });
    }
};

let OwlMixin = {
    _initalizeOwlSlider: function (ppr) {
        let responsive = {0: {items: 1}, 576: {items: 2}, 768: {items: 3}, 992: {items: 3}, 1200: {items: ppr}};
        if (this.$('.s_d_horizontal_card').length) {
            responsive = {0: {items: 1}, 576: {items: ppr}};
        }
        this.$('.droggol_product_slider').owlCarousel({
            dots: false,
            margin: 20,
            stagePadding: 5,
            rewind: true,
            rtl: _t.database.parameters.direction === 'rtl',
            nav: true,
            navText: ['<i class="dri dri-arrow-left-l"></i>', '<i class="dri dri-arrow-right-l"></i>'],
            responsive: responsive
        });
    }
};

let ProductsBlockMixins = {
    _setCamelizeAttrs: function () {
        this._super.apply(this, arguments);
        this.selectionType = false;
        if (this.productsParams) {
            this.selectionType = this.productsParams.selectionType;
        }
    },
    /**
    * @private
    */
    _getDomain: function () {
        let domain = false;
        switch (this.selectionType) {
            case 'manual':
                if (this.productsParams.productIDs.length) {
                    domain = [['id', 'in', this.productsParams.productIDs]];
                }
                break;
            case 'advance':
                if (_.isArray(this.productsParams.domain_params.domain)) {
                    domain = this.productsParams.domain_params.domain;
                }
                break;
        }
        return domain ? domain : this._super.apply(this, arguments);
    },
    /**
    * @private
    */
    _getLimit: function () {
        return (this.selectionType === 'advance' ? this.productsParams.domain_params.limit || 5 : this._super.apply(this, arguments));
    },
    /**
    * @private
    */
    _getSortBy: function () {
        return (this.selectionType === 'advance' ? this.productsParams.domain_params.sortBy : this._super.apply(this, arguments));
    },
    /**
    * @private
    */
    _getProducts: function (data) {
        let {products} = data;
        let productsParams = this.productsParams;
        if (productsParams && productsParams.selectionType === 'manual') {
            products = _.map(productsParams.productIDs, function (productID) {
                return _.findWhere(data.products, {id: productID}) || false;
            });
        }
        return _.compact(products);
    },
    /**
    * @private
    */
    _processData: function (data) {
        this._super.apply(this, arguments);
        return this._getProducts(data);
    },
};

let HotspotMixns = {
    _getHotspotConfig: function () {
        if (this.$target.get(0).dataset.hotspotType === 'static') {
            return {titleText: this.$target.get(0).dataset.titleText, subtitleText: this.$target.get(0).dataset.subtitleText, buttonLink: this.$target.get(0).dataset.buttonLink, hotspotType: this.$target.get(0).dataset.hotspotType, buttonText: this.$target.get(0).dataset.buttonText, imageSrc: this.$target.get(0).dataset.imageSrc};
        }
        return {};
    },
    _isPublicUser: function () {
        return _.has(odoo.dr_theme_config, "is_public_user") && odoo.dr_theme_config.is_public_user;
    },

    _cleanNodeAttr: function () {
        if (this._isPublicUser()) {
            let attrs = ['data-image-src', 'data-hotspot-type', 'data-title-text', 'data-subtitle-text', 'data-button-link', 'data-button-text', 'data-top', 'data-on-hotspot-click'];
            attrs.forEach(attr => {this.$target.removeAttr(attr)});
        }
    },
};

let ProductsMixin = {
    /**
     * @param {Array} productIDs
     * @private
     */
    _fetchProductsData: function (productIDs) {
        let params = {
            domain: [['id', 'in', productIDs]],
            fields: ['name', 'price', 'description_sale', 'website_published', 'dr_label_id'],
       };
        return this._rpc({
            route: '/theme_prime/get_products_data',
            params: params,
        });
    },
};
let CategoryPublicWidgetMixins = {

    _setCamelizeAttrs: function () {
        this._super.apply(this, arguments);
        if (this.categoryParams) {
            var categoryIDs = this.categoryParams.categoryIDs;
            // first category
            this.initialCategory = categoryIDs.length ? categoryIDs[0] : false;
        }
    },
    /**
     * @private
     * @returns {Array} options
     */
    _getOptions: function () {
        var options = this._super.apply(this, arguments) || {};
        if (!this.initialCategory) {
            return false;
        }
        var categoryIDs = this.categoryParams.categoryIDs;
        options['order'] = this._getParsedSortBy(this.categoryParams.sortBy);
        options['limit'] = this.categoryParams.limit;
        // category name id vadi dict first time filter render karva mate
        options['get_categories'] = true;
        options['categoryIDs'] = categoryIDs;
        options['categoryID'] = this.initialCategory;
        return options;
    },
    /**
     * @private
     * @returns {Array} domain
     */
    _getDomain: function () {
        if (!this.initialCategory) {
            return false;
        }
        var operator = '=';
        if (this.categoryParams.includesChild) {
            operator = 'child_of';
        }
        return [['public_categ_ids', operator, this.initialCategory]];
    },
};

var CartManagerMixin = {

    _handleCartConfirmation: function (cartFlow, data) {
        var methodName = _.str.sprintf('_cart%s', _.str.classify(cartFlow));
        return this[methodName](data);
    },

    _cartNotification: function (data) {

        return this.displayNotification({
            Notification: DroggolNotification,
            sticky: true,
            type: 'abcd',
            message: qweb.render('DroggolAddToCartNotification', {name: data.product_name}),
            className: 'd_notification d_notification_primary',
            d_image: _.str.sprintf('/web/image/product.product/%s/image_256', this.rootProduct.product_id),
            buttons: [{text: _t('View cart'), class: 'btn btn-link btn-sm p-0', link: true, href: '/shop/cart'}]
        });
    },

    _cartDialog: function (data) {
        new ConfirmationDialog(this, {data: data, size: 'medium'}).open();
    },

    _cartSideCart: function (data) {
        new CartSidebar(this).open();
    },
};

return {
    DroggolUtils: DroggolUtils,
    HotspotMixns: HotspotMixns,
    SortableMixins: SortableMixins,
    ProductCarouselMixins: ProductCarouselMixins,
    CategoryMixins: CategoryMixins,
    CategoryPublicWidgetMixins: CategoryPublicWidgetMixins,
    OwlMixin: OwlMixin,
    CategoryWidgetMixins: CategoryWidgetMixins,
    ProductsBlockMixins: ProductsBlockMixins,
    ProductsMixin: ProductsMixin,
    CartManagerMixin: CartManagerMixin,
    cartMixin: cartMixin
};
});
