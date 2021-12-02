odoo.define('theme_prime.drift_zoom', function (require) {
'use strict';

require('website_sale.website_sale');
var publicWidget = require('web.public.widget');
const { _t } = require('web.core');

publicWidget.registry.WebsiteSale.include({
    _startZoom: function () {
        // Disable zoomOdoo, Because we have Drift
    },
});

publicWidget.registry.TpDriftZoom = publicWidget.Widget.extend({
    selector: '.tp-drift-zoom',
    disabledInEditableMode: true,
    start: function () {
        const className = _t.database.parameters.direction === 'rtl' ? 'tp-rtl' : 'tp';
        // If option is activated then zoom
        var zoomConfig = odoo.dr_theme_config.json_zoom;
        if (zoomConfig.zoom_enabled) {
            this.images = _.map(this.$('.tp-drift-zoom-img'), function (el) {
                var imageVals = {namespace: className, sourceAttribute: 'src', inlineOffsetY: -50, paneContainer: el.parentElement, zoomFactor: zoomConfig.zoom_factor || 2, inlinePane: 992, touchDelay: 500};
                var bigImage = $(el).attr('data-zoom-image');
                if (bigImage) {
                    imageVals.sourceAttribute = 'data-zoom-image';
                }
                if (zoomConfig.disable_small && !bigImage) {
                    return false;
                }
                return new Drift(el, imageVals);
            });
        }
        return this._super.apply(this, arguments);
    },
    destroy: function () {
        _.invoke(_.compact(this.images), 'disable');
        this._super.apply(this, arguments);
    }
});

});
