odoo.define('theme_prime.website_root', function (require) {
'use strict';

const WebsiteRoot = require('website.root').WebsiteRoot;

var TpWebsiteRoot = WebsiteRoot.include({
    events: _.extend({}, WebsiteRoot.prototype.events || {}, {
        'click .dropdown-menu .tp-select-pricelist': '_onClickTpPricelist',
        'change .dropdown-menu .tp-select-pricelist': '_onChangeTpPricelist',
    }),
    _onClickTpPricelist: function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
    },
    _onChangeTpPricelist: function (ev) {
        const value = $(ev.currentTarget).val();
        window.location = value;
    },
});

return TpWebsiteRoot;

});
