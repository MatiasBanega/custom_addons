odoo.define('theme_prime.product.root.widget', function (require) {
'use strict';

require('website_sale.utils');
const config = require('web.config');
const {qweb, _t} = require('web.core');
const RootWidget = require('theme_prime.root.widget');
const DroggolNotificationManger = require('theme_prime.notification.manger');
const QuickViewDialog = require('theme_prime.product_quick_view');
const {cartMixin} = require('theme_prime.mixins');

return RootWidget.extend(cartMixin, {

    xmlDependencies: (RootWidget.prototype.xmlDependencies || []).concat(['/theme_prime/static/src/xml/frontend/notification_template.xml']),

    snippetNodeAttrs: (RootWidget.prototype.snippetNodeAttrs || []).concat(['data-user-params']),

    read_events: {
        'click .d_add_to_cart_btn': '_onAddToCartClick',
        'click .d_add_to_wishlist_btn': '_onAddtoWishlistClick',
        'click .d_product_quick_view': '_onProductQuickViewClick',
        'mouseenter .d_product_thumb_img': '_onMouseEnter',
    },

    //--------------------------------------------------------------------------
    // Khangi/Private
    //--------------------------------------------------------------------------

    /**
    * @private
    */
    _getOptions: function () {
        let options = {};
        // add new attribute to widget or just set data-userParams to $target
        if (this.userParams) {
            if (this.userParams.wishlist) {
                options['wishlist_enabled'] = true;
            }
            // fetch shop config only if 'wishlist', 'comparison', 'rating'
            // any one of this is enabled in current snippet
            if (this._anyActionEnabled(this._getMustDisabledOptions())) {
                options['shop_config_params'] = true;
            }
            return options;
        } else {
            return this._super.apply(this, arguments);
        }
    },
    /**
    * Check any given option is enabled(true) in userParams.
    * e.g. this.userParams.wishlist = true;
    * this method return true if any one of given option is true
    * @private
    */
    _anyActionEnabled: function (options) {
        return _.contains(_.values(_.pick(this.userParams, options)), true);
    },
    /**
     * @private
     */
    _getAllActions: function () {
        return ['wishlist', 'comparison', 'add_to_cart', 'quick_view'];
    },
    /**
    * @private
    * @see _getMustDisabledOptions of configurator
    */
    _getMustDisabledOptions: function () {
        return ['wishlist', 'comparison', 'rating'];
    },
    /**
     * init tooltips
     *
     * @private
     */
    _initTips: function () {
        this.$('[data-toggle="tooltip"]').tooltip();
    },
    /**
     * @override
     */
    _modifyElementsAfterAppend: function () {
        let self = this;
        this._initTips();
        _.each(this.wishlistProductIDs, function (id) {
            self.$('.d_add_to_wishlist_btn[data-product-product-id="' + id + '"]').prop("disabled", true).addClass('disabled');
        });
        // [HACK] must be improve in next version.
        // Dev like it will work on both (shop and snippet)
        // Also in snippet only show similar_products buttons if similar_products exist
        if (this.userParams && this.userParams.show_similar) {
            this.trigger_up('widgets_start_request', {$target: this.$('.tp_show_similar_products')});
        }
        this._super.apply(this, arguments);
    },
    /**
     * @private
     */
    _updateUserParams: function (shopConfigParams) {
        let self = this;
        if (this.userParams) {
            _.each(this._getMustDisabledOptions(), function (option) {
                let enabledInShop = shopConfigParams['is_' + option + '_active'];
                if (!enabledInShop) {
                    self.userParams[option] = false;
                }
            });
            // whether need to render whole container for
            // e.g if all actions are disabled then donot render overlay(contains add to card, wishlist btns etc)
            this.userParams['anyActionEnabled'] = this._anyActionEnabled(this._getAllActions());
        }
    },
    /**
    * Method is copy of wishlist public widget
    *
    * @private
    */
    _updateWishlistView: function () {
        if (this.wishlistProductIDs.length > 0) {
            $('.o_wsale_my_wish').show();
            $('.my_wish_quantity').text(this.wishlistProductIDs.length);
        } else {
            $('.o_wsale_my_wish').show();
            $('.my_wish_quantity').text('');
        }
    },
    /**
    * @private
    */
    _setDBData: function (data) {
        if (data.wishlist_products) {
            this.wishlistProductIDs = data.wishlist_products;
        }
        if (data.shop_config_params) {
            this._updateUserParams(data.shop_config_params);
        }
        this._super.apply(this, arguments);
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param  {Event} ev
     */
    _onAddToCartClick: function (ev) {
        this.onAddToCartClick(ev, QuickViewDialog);
    },
    /**
     * @private
     * @param  {Event} ev
     */
    _onProductQuickViewClick: function (ev) {
        // set $parentNode to fix bug
        this.QuickViewDialog = new QuickViewDialog(this, {
            productID: parseInt($(ev.currentTarget).attr('data-product-template-id')),
        });
        this.QuickViewDialog.open();
    },
    /**
    * @private
    */
    _removeProductFromWishlist: function (wishlistID, productID) {
        this._rpc({
            route: '/shop/wishlist/remove/' + wishlistID,
        }).then(() => {
            $(".d_add_to_wishlist_btn[data-product-product-id='" + productID + "']").prop("disabled", false).removeClass('disabled');
            this.wishlistProductIDs = _.filter(this.wishlistProductIDs, function (id) {
                 return id !== productID;
             });
            this._updateWishlistView();
        });
    },
    /**
     * @private
     * @param  {Event} ev
     */
    _onAddtoWishlistClick: function (ev) {
        let productID = parseInt($(ev.currentTarget).attr('data-product-product-id'));
        this._rpc({
            route: '/theme_prime/wishlist_general',
            params: {
                product_id: productID,
            },
        }).then(res => {
            this.wishlistProductIDs = res.products;
            this.displayNotification({
                Notification: DroggolNotificationManger,
                sticky: false,
                type: 'abcd',
                message: qweb.render('DroggolWishlistNotification', {name: res.name}),
                className: 'd_notification d_notification_danger',
                d_image: _.str.sprintf('/web/image/product.product/%s/image_256', productID),
                buttons: [{
                    text: _t('See your wishlist'),
                    class: 'btn btn-link btn-sm p-0',
                    link: true,
                    href: '/shop/wishlist'
                    }, {
                    text: _t('Undo'),
                    class: 'btn btn-link btn-sm float-right',
                    click: this._removeProductFromWishlist.bind(this, res.wishlist_id, productID),
                }]
            });
            this._updateWishlistView();
            $(".d_add_to_wishlist_btn[data-product-product-id='" + productID + "']").prop("disabled", true).addClass('disabled');
        });
    },
    /**
     * @private
     */
    _onMouseEnter: function (ev) {
        let $target = $(ev.currentTarget);
        let src = $target.attr('src');
        let productID = $target.attr('data-product-id');
        let $card = this.$('.d_product_card[data-product-id=' + productID + ']');
        $card.find('.d-product-img').attr('src', src);
        $card.find('.d_product_thumb_img').removeClass('d_active');
        $target.addClass('d_active');
    },
    _cleanBeforeAppend: function () {
        if (this.userParams && this.userParams.layoutType === 'grid') {
            this._setClass();
        }
    },
    _onWindowResize: function () {
        this._super.apply(this, arguments);
        if (this.userParams && this.userParams.layoutType === 'grid') {
            this._setClass();
            this._onSuccessResponse(this.response);
        }
    },
    _setClass: function () {
        let device = config.device;
        this.deviceSizeClass = device.size_class;
        if (this.deviceSizeClass <= 1) {
            this.cardSize = 12;
            this.cardColClass = 'col-' + this.cardSize.toString();
        } else if (this.deviceSizeClass === 2) {
            this.cardSize = 6;
            this.cardColClass = 'col-sm-' + this.cardSize.toString();
        } else if (this.deviceSizeClass === 3 || this.deviceSizeClass === 4) {
            this.cardSize = 4;
            this.cardColClass = 'col-md-' + this.cardSize.toString();
        } else if (this.deviceSizeClass >= 5) {
            this.cardSize = parseInt(12 / this.userParams.ppr);
            this.cardColClass = 'col-lg-' + this.cardSize.toString();
        }
    }
});

});
