odoo.define('theme_prime.recently_viewed', function (require) {
'use strict';

require('website_sale.recently_viewed');
let publicWidget = require('web.public.widget');
let {qweb} = require('web.core');
let config = require('web.config');

publicWidget.registry.productsRecentlyViewedSnippet.include({
    xmlDependencies: (publicWidget.registry.productsRecentlyViewedSnippet.prototype.xmlDependencies || []).concat(['/theme_prime/static/src/xml/recently_viewed_products.xml']),
    _render: function (res) {
        var gridSize =  [2, 2, 3, 3, 4, 6, 6][config.device.size_class] || 2;
        var products = res['products'];
        var mobileProducts = [], webProducts = [], productsTemp = [];
        _.each(products, function (product, index) {
            if (productsTemp.length === gridSize) {
                webProducts.push(productsTemp);
                productsTemp = [];
            }
            productsTemp.push(product);
            if (index % 2 === 0) {
                let mobile = [product];
                if (products[index + 1]) {
                    mobile.push(products[index + 1]);
                }
                mobileProducts.push(mobile);
            }
        });
        if (productsTemp.length) {
            webProducts.push(productsTemp);
        }

        this.mobileCarousel = $(qweb.render('website_sale.productsRecentlyViewed', {uniqueId: this.uniqueId, productFrame: 2, productsGroups: mobileProducts}));
        this.webCarousel = $(qweb.render('website_sale.productsRecentlyViewed', {uniqueId: this.uniqueId, productFrame: gridSize, productsGroups: webProducts}));
        this._addCarousel();
        this.$el.toggleClass('d-none', !(products && products.length));
        if (config.device.isMobile) {
            this.$('.o_carousel_product_card_wrap').addClass('col-6');
        }
    },
});

});
