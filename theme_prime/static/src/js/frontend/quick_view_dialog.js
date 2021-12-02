odoo.define('theme_prime.product_quick_view', function (require) {
'use strict';

require('website_sale_comparison.comparison');
const ajax = require('web.ajax');
const Dialog = require('web.Dialog');
const publicWidget = require('web.public.widget');
const {ProductCarouselMixins} = require('theme_prime.mixins');


let QuickViewDialog = Dialog.extend(ProductCarouselMixins, {
    xmlDependencies: Dialog.prototype.xmlDependencies.concat(
        ['/theme_prime/static/src/xml/frontend/quick_view.xml']
    ),
    template: 'theme_prime.product_quick_view',
    events: _.extend({}, Dialog.prototype.events, {
        'dr_close_dialog': 'close'
    }),
    /**
     * @constructor
     */
    init: function (parent, options) {
        this.productID = options.productID;
        this.mini = options.mini || false;
        this.variantID = options.variantID || false;
        this.add_if_single_variant = options.add_if_single_variant || false;
        this._super(parent, _.extend({renderHeader: false, renderFooter: false, technical: false, size: 'extra-large', backdrop: true}, options || {}));
    },
    /**
     * @override
     */
    start: function () {
        var sup = this._super.apply(this, arguments);
        // Append close button to dialog
        $('<button/>', {class: 'close', 'data-dismiss': "modal", html: '<i class="fa fa-times"/>'}).prependTo(this.$modal.find('.modal-content'));
        this.$modal.find('.modal-dialog').addClass('modal-dialog-centered d_product_quick_view_dialog dr_full_dialog');
        if (this.mini) {
            this.$modal.find('.modal-dialog').addClass('is_mini');
        }
        ajax.jsonRpc('/theme_prime/get_quick_view_html', 'call', {
            options: {productID: this.productID, variantID: this.variantID,mini: this.mini}
        }).then(data => {
            this.$el.find('.d_product_quick_view_loader').replaceWith(data);
            this._updateIDs(this.$el);
            this.trigger_up('widgets_start_request', {
                $target: this.$('.oe_website_sale'),
            });
        });
        return sup;
    },
});

publicWidget.registry.d_product_quick_view = publicWidget.Widget.extend({
    selector: '.tp-product-quick-view-action, .tp_hotspot[data-on-hotspot-click="modal"]',
    read_events: {
        'click': '_onClick',
    },
    /**
     * @private
     * @param  {Event} ev
     */
    _onClick: function (ev) {
        this.QuickViewDialog = new QuickViewDialog(this, {
            productID: parseInt($(ev.currentTarget).attr('data-product-id'))
        }).open();
    },
});

return QuickViewDialog;

});
