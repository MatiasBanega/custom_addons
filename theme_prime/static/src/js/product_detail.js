odoo.define('theme_prime.product_detail', function (require) {
'use strict';

require('website_sale.website_sale');
const publicWidget = require('web.public.widget');
const Dialog = require('web.Dialog');
const { ProductCarouselMixins } = require('theme_prime.mixins');


publicWidget.registry.TpProductRating = publicWidget.Widget.extend({
    selector: '.tp-product-rating',
    events: {
        'click': '_onClickProductRating',
    },
    _onClickProductRating: function () {
        $('.nav-link[href="#tp-product-rating-tab"]').click();
        $('html, body').animate({scrollTop: $('.tp-product-details-tab').offset().top});
    }
});

publicWidget.registry.TpProductOffers = publicWidget.Widget.extend({
    selector: '.dr-product-offers',
    events: {
        'click': '_onClickProductOffers',
    },
    init: function () {
        this.dialogContent = false;
        this._super.apply(this, arguments);
    },
    _onClickProductOffers: function (ev) {
        ev.preventDefault();
        this._getDialogContent().then(result => {
            this.offerPopup = new Dialog(this, {
                technical: false, $content: $('<div/>').html(result), dialogClass: 'p-0', renderFooter: false
            });

            this.offerPopup.opened().then(() => {
                var $offerModal = this.offerPopup.$modal;
                $offerModal.find('.modal-dialog').addClass('modal-dialog-centered');
                $offerModal.addClass('dr_offer_dialog');
                this.trigger_up('widgets_start_request', {
                    $target: $offerModal, editableMode: this.editableMode
                });
            });

            this.offerPopup.open();
        });
    },
    _getDialogContent: function () {
        var dialogId = this.$target.data('id');
        if (this.dialogContent) {
            return Promise.resolve(this.dialogContent);
        } else {
            return this._rpc({
                route: '/theme_prime/get_offer_dialog_content',
                params: {dialog_id: dialogId},
            }).then(result => {
                if (result && result[0].dialog_content) {
                    this.dialogContent = result[0].dialog_content;
                }
                return this.dialogContent;
            });
        }
    }
});


// TODO: Move below code to core files
publicWidget.registry.WebsiteSale.include({
    _updateProductImage: function ($productContainer, displayImage, productId, productTemplateId, newCarousel, isCombinationPossible) {
        var $carousel = $productContainer.find('.d_shop_product_details_carousel');
        if ($carousel.length) {
            if (window.location.search.indexOf('enable_editor') === -1) {
                var $newCarousel = $(newCarousel);
                $carousel.after($newCarousel);
                $carousel.remove();
                $carousel = $newCarousel;
                $carousel.carousel(0);
                this._startZoom();
                this.trigger_up('widgets_start_request', {$target: $carousel});
                ProductCarouselMixins._updateIDs($productContainer);
            }
            $carousel.toggleClass('css_not_available', !isCombinationPossible);
        } else {
            $carousel = $productContainer.find('#o-carousel-product');
            this._super.apply(this, arguments);
        }

        let $container = $productContainer.parents('.tp-show-variant-image');
        if ($container.length) {
            let src = $carousel.find('.tp-drift-zoom-img:first').attr('src');
            if (src !== $container.find('.tp-variant-image').attr('src')) {
                $container.find('.tp-variant-image').fadeOut(400);
                _.delay(function () {$container.find('.tp-variant-image').attr('src', src).fadeIn(650);}, 400);
            }
        }
    },
});

});
