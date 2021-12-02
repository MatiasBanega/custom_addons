odoo.define('theme_prime.product_searchbar', function (require) {
'use strict';

require('website_sale.s_products_searchbar');
const publicWidget = require('web.public.widget');

publicWidget.registry.productsSearchBar.include({
    xmlDependencies: (publicWidget.registry.productsSearchBar.prototype.xmlDependencies || []).concat(
        ['/theme_prime/static/src/xml/product_searchbar.xml']
    ),
    events: _.extend({}, publicWidget.registry.productsSearchBar.prototype.events, {
        'click .tp-category-dropdown-container .dropdown-item': '_onClickCategory',
        'click .tp-category-dropdown-container': '_onClickDropdown',
    }),
    _onClickDropdown: function (ev) {
        var self = this;
        this.$('.tp-category-dropdown-container').on('show.bs.dropdown', function () {
            self.$target.children('.dropdown-menu').remove();
        });
        this._render();
    },
    _onClickCategory: function (ev) {
        ev.preventDefault();
        var $item = $(ev.currentTarget);
        this.categoryID = $item.data('id') || false;
        this.$('.tp-active-text').text($item.text());
        var actionURL = '/shop';
        if (this.categoryID) {
            actionURL = _.str.sprintf('/shop/category/%s', this.categoryID);
        }
        this.$('.search-query').val('');
        this.$el.attr('action', actionURL);
    },
    _fetch: function () {
        var options = {'order': this.order, 'limit': this.limit, 'display_description': this.displayDescription, 'display_price': this.displayPrice, 'max_nb_chars': Math.round(Math.max(this.autocompleteMinWidth, parseInt(this.$el.width())) * 0.22)};
        if (this.categoryID) {
            options['category'] = this.categoryID;
        }
        return this._rpc({
            route: '/shop/products/autocomplete',
            params: {
                'term': this.$input.val(),
                'options': options,
            },
        });
    },
    _onInput: function (ev) {
        if (this.$('.tp-category-dropdown').hasClass('show')) {
            this.$('.tp-category-dropdown .show').removeClass('show');
        }
        if (!$(ev.currentTarget).val()) {
            this._render();
            return;
        } else {
            this._super.apply(this, arguments);
        }
    },
});

});
