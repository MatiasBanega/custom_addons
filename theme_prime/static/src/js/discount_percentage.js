odoo.define('theme_prime.discount_percentage', function (require) {
'use strict';

require('website_sale.website_sale');

const publicWidget = require('web.public.widget');
const {_t} = require('web.core');

publicWidget.registry.WebsiteSale.include({
    _onChangeCombination: function (ev, $parent, combination) {
        this._super.apply(this, arguments);

        const $price = $parent.find('.oe_price_h4');
        let $percentage = $parent.find('.tp-discount-percentage');

        if (combination.has_discounted_price) {
            const percentage = Math.round((combination.list_price - combination.price) / combination.list_price * 100);
            if (percentage) {
                const percentageText = _.str.sprintf(_t('(%d%% OFF)'), percentage);
                if ($percentage.length) {
                    $percentage.text(percentageText);
                } else {
                    $percentage = $('<small class="tp-discount-percentage d-none d-md-inline-block ml-1">' + percentageText + '</small>');
                    $percentage.appendTo($price);
                }
            } else {
                $percentage.remove();
            }
        } else {
            $percentage.remove();
        }
    },
});

});
