odoo.define('theme_prime.cart_sidebar', function (require) {
'use strict';

require('website_sale.cart');
var publicWidget = require('web.public.widget');
var wSaleUtils = require('website_sale.utils');
var Widget = require('web.Widget');

var Sidebar = Widget.extend({
    events: _.extend({}, Widget.prototype.events, {
        'click .tp-close': 'close',
    }),
    init: function (parent, options) {
        this._super(parent);
        var self = this;
        this._opened = new Promise(function (resolve) {
            self._openedResolver = resolve;
        });
        options = _.defaults(options || {});
        this.$content = options.$content;
        this.leftSide = options.leftSide ? 'left': 'right';
        this.sidebarClass = options.sidebarClass || " " ;
        this.$backdrop = $('<div class="modal-backdrop tp-sidebar-backdrop show d-block"/>');
        this.$backdrop.on('click', this._onClickBackdrop.bind(this));
    },
    renderElement: function () {
        this._super.apply(this, arguments);
        if (this.$content) {
            this.setElement(this.$content);
        }
    },
    open: function (options) {
        var self = this;
        self.$backdrop.appendTo('body');
        $('body').addClass('modal-open');
        this.appendTo($('<div/>')).then(function () {
            self.$el.appendTo('body')
            self.$el.addClass('tp-sidebar ' + self.leftSide + ' '+ self.sidebarClass);
            self._openedResolver();
            setTimeout(() => {self.$el.addClass('open');}, 100);
        });
        return self;
    },
    opened: function (handler) {
        return (handler)? this._opened.then(handler) : this._opened;
    },
    _onClickBackdrop: function (ev) {
        ev.preventDefault();
        this.close();
    },
    close: function () {
        this.$el.removeClass('open');
        this.$backdrop.remove();
        $('body').removeClass('modal-open');
        this.$el.remove();
    },
});

var CartSidebar = Sidebar.extend({
    events: _.extend({}, Sidebar.prototype.events, {
        'click .tp-remove-line': '_onRemoveLine',
    }),
    willStart: function () {
        var proms = [this._super.apply(this, arguments)];
        proms.push(this._getTemplate().then(template => this.$content = $(template)));
        return Promise.all(proms);
    },
    _getTemplate: function () {
        return $.get('/shop/cart', { type: 'tp_cart_sidebar_request' });
    },
    _onRemoveLine: function (ev) {
        ev.preventDefault();
        const lineID = $(ev.currentTarget).data('line-id');
        const productID = $(ev.currentTarget).data('product-id');
        return this._rpc({
            route: '/shop/cart/update_json',
            params: {line_id: lineID, product_id: productID, set_qty: 0}
        }).then(this._refreshCart.bind(this));
    },
    async _refreshCart (data) {
        data['cart_quantity'] = data.cart_quantity || 0;
        wSaleUtils.updateCartNavBar(data);
        const template = await this._getTemplate();
        this.$el.children().remove();
        $(template).children().appendTo(this.$el);
    },
    _onCartSidebarClose: function () {
        this.close();
    },
});

// Disable cart popover
publicWidget.registry.websiteSaleCartLink.include({
    selector: '#top_menu a[href$="/shop/cart"]:not(.tp-cart-sidebar-action)',
});

publicWidget.registry.TpCartSidebarBtn = publicWidget.Widget.extend({
    selector: '.tp-cart-sidebar-action',
    read_events: {
        'click': '_onClick',
    },
    _onClick: function (ev) {
        ev.preventDefault();
        new CartSidebar(this).open();
    },
});

var SearchSidebar = Sidebar.extend({
    willStart: function () {
        var proms = [this._super.apply(this, arguments)];
        proms.push(this._getTemplate().then(template => this.$content = $(template)));
        return Promise.all(proms);
    },
    _getTemplate: function () {
        return $.get('/theme_prime/search_sidebar');
    },
    start: function () {
        var self = this;
        return this._super.apply(this, arguments).then(function () {
            self.trigger_up('widgets_start_request', {
                $target: self.$('.o_wsale_products_searchbar_form'),
            });
        });
    },
});

publicWidget.registry.TpSearchSidebarBtn = publicWidget.Widget.extend({
    selector: '.tp-search-sidebar-action',
    read_events: {
        'click': '_onClick',
    },
    _onClick: function (ev) {
        ev.preventDefault();
        new SearchSidebar(this).open();
    },
});

var CategorySidebar = Sidebar.extend({
    willStart: function () {
        var proms = [this._super.apply(this, arguments)];
        proms.push(this._getTemplate().then(template => this.$content = $(template)));
        return Promise.all(proms);
    },
    _getTemplate: function () {
        return $.get('/theme_prime/get_category_sidebar');
    },
});

publicWidget.registry.TpCategorySidebarBtn = publicWidget.Widget.extend({
    selector: '.tp-category-action',
    read_events: {
        'click': '_onClick',
    },
    _onClick: function (ev) {
        ev.preventDefault();
        new CategorySidebar(this, {sidebarClass: ' bg-100'}).open();
    },
});

var similarProductsSidebar = Sidebar.extend({
    init: function (parent, options) {
        this._super.apply(this, arguments);
        this.productID = options.productID;
    },
    willStart: function () {
        var proms = [this._super.apply(this, arguments)];
        proms.push(this._getTemplate().then(template => this.$content = $(template)));
        return Promise.all(proms);
    },
    _getTemplate: function () {
        return $.get('/theme_prime/get_similar_products_sidebar', {productID: this.productID});
    },
});

publicWidget.registry.TpShowSimilarProducts = publicWidget.Widget.extend({
    selector: '.tp_show_similar_products',
    read_events: {
        'click': '_onClick',
    },
    _onClick: function (ev) {
        ev.preventDefault();
        new similarProductsSidebar(this, { sidebarClass: ' bg-100', productID: parseInt($(ev.currentTarget).attr('data-product-template-id'))}).open();
    },
});

return {
    Sidebar: Sidebar,
    CartSidebar: CartSidebar,
    SearchSidebar: SearchSidebar,
};

});
