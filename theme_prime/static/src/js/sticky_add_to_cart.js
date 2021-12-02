odoo.define('theme_prime.sticky_add_to_cart', function (require) {
'use strict';

require('website_sale.website_sale');

var publicWidget = require('web.public.widget');
var config = require('web.config');
const sAnimations = require('website.content.snippets.animation');
const isMobileEnv = config.device.size_class <= config.device.SIZES.LG && config.device.touch;

publicWidget.registry.WebsiteSale.include({
    _onChangeCombination: function (ev, $parent, combination) {
        this._super.apply(this, arguments);
        const $stickyAddToCart = $('.tp-sticky-add-to-cart');

        if ($stickyAddToCart.length) {
            $stickyAddToCart.find('.oe_currency_value').text(this._priceToStr(combination.price));
            $stickyAddToCart.find('.product-img').attr('src', '/web/image/product.product/' + combination.product_id + '/image_128');

            $stickyAddToCart.find('.product-add-to-cart').removeClass('disabled');
            if (['always', 'threshold'].includes(combination.inventory_availability)) {
                if (!combination.virtual_available) {
                    $stickyAddToCart.find('.product-add-to-cart').addClass('disabled');
                }
            }
        }
    },
});

sAnimations.registry.TpStickyAddToCart = sAnimations.Animation.extend({
    selector: '.tp-sticky-add-to-cart',
    disabledInEditableMode: true,
    effects: [{
        startEvents: 'scroll',
        update: '_onScroll',
    }],
    events: {
        'click .product-add-to-cart': '_onClickProductAddToCart',
        'click .product-img': '_onClickImg'
    },
    _onScroll: function () {
        if (!isMobileEnv && $('#add_to_cart').length) {
            if ($('#add_to_cart')[0].getBoundingClientRect().top <= 0) {
                this.$el.fadeIn();
            } else {
                this.$el.fadeOut();
            }
        }
    },
    _onClickProductAddToCart: function (ev) {
        ev.preventDefault();
        $('#add_to_cart').click();
    },
    _onClickImg: function (ev) {
        ev.preventDefault();
        $('html, body').animate({ scrollTop: 0 });
    }
});

});
